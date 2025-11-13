# Standard library imports
import logging

# Imports of odoo
from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class L10nClCafAuto(models.Model):
    _name = "l10n_cl.caf.auto"
    _description = "Automatic CAF Monitoring"
    _order = "create_date desc"

    # Fields
    name = fields.Char(
        string="Name",
        compute="_compute_name",
        store=True,
        readonly=True,
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )
    document_type_id = fields.Many2one(
        "l10n_latam.document.type",
        string="Document Type",
        required=True,
        domain="[('country_id.code', '=', 'CL')]",
    )
    threshold_percentage = fields.Float(
        string="Alert Threshold (%)",
        default=20.0,
        help="Alert when remaining folios are below this percentage",
    )
    threshold_absolute = fields.Integer(
        string="Alert Threshold (Absolute)",
        default=50,
        help="Alert when remaining folios are below this number",
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )
    alert_user_ids = fields.Many2many(
        "res.users",
        string="Alert Users",
        help="Users to notify when threshold is reached",
    )
    last_check_date = fields.Datetime(
        string="Last Check Date",
        readonly=True,
    )
    last_alert_date = fields.Datetime(
        string="Last Alert Date",
        readonly=True,
    )

    # Compute methods
    @api.depends("document_type_id", "company_id")
    def _compute_name(self):
        for record in self:
            if record.document_type_id:
                record.name = _("CAF Monitor: %s - %s") % (
                    record.company_id.name,
                    record.document_type_id.name,
                )
            else:
                record.name = _("CAF Monitor")

    # Business methods
    def check_caf_availability(self):
        """Check CAF availability and send alerts if needed.

        This method checks the available CAF folios for the document type
        and sends alerts to configured users if the threshold is reached.

        :return: True if check successful
        """
        self.ensure_one()

        # Get available CAF files for this document type
        caf_model = self.env["l10n_cl.dte.caf"]
        available_cafs = caf_model.search(
            [
                ("company_id", "=", self.company_id.id),
                ("l10n_latam_document_type_id", "=", self.document_type_id.id),
                ("status", "=", "in_use"),
            ]
        )

        if not available_cafs:
            self._send_alert(
                _("No CAF files available for document type %s")
                % self.document_type_id.name
            )
            return True

        # Calculate total available folios
        total_available = sum(caf.final_nb - caf.start_nb + 1 for caf in available_cafs)

        # Get used folios count from existing invoices
        move_model = self.env["account.move"]
        last_used = move_model.search(
            [
                ("company_id", "=", self.company_id.id),
                ("l10n_latam_document_type_id", "=", self.document_type_id.id),
                ("l10n_latam_document_number", "!=", False),
            ],
            order="l10n_latam_document_number desc",
            limit=1,
        )

        if last_used:
            current_folio = int(last_used.l10n_latam_document_number)
            remaining = max(caf.final_nb for caf in available_cafs) - current_folio
        else:
            remaining = total_available

        # Check thresholds
        percentage_remaining = (
            (remaining / total_available * 100) if total_available > 0 else 0
        )

        if (
            remaining < self.threshold_absolute
            or percentage_remaining < self.threshold_percentage
        ):
            self._send_alert(
                _("Low CAF availability for %s: %s folios remaining (%.1f%%).")
                % (self.document_type_id.name, remaining, percentage_remaining)
            )

        self.last_check_date = fields.Datetime.now()
        return True

    def _send_alert(self, message):
        """Send alert to configured users.

        :param message: Alert message to send
        """
        self.ensure_one()

        if not self.alert_user_ids:
            _logger.warning("No alert users configured for %s", self.name)
            return

        # Create activity for each alert user
        for user in self.alert_user_ids:
            self.env["mail.activity"].create(
                {
                    "activity_type_id": self.env.ref(
                        "mail.mail_activity_data_warning"
                    ).id,
                    "summary": _("CAF Alert: %s") % self.document_type_id.name,
                    "note": message,
                    "user_id": user.id,
                    "res_id": self.id,
                    "res_model_id": self.env["ir.model"]._get_id(self._name),
                }
            )

        self.last_alert_date = fields.Datetime.now()
        _logger.info("CAF alert sent: %s", message)

    @api.model
    def cron_check_caf_availability(self):
        """Cron job to check CAF availability for all active monitors.

        This method is called by scheduled action to automatically
        check CAF availability and send alerts if needed.
        """
        monitors = self.search([("active", "=", True)])
        for monitor in monitors:
            try:
                monitor.check_caf_availability()
            except Exception as error:
                _logger.error(
                    "Error checking CAF availability for %s: %s",
                    monitor.name,
                    error,
                )
