(function($) {

	// Met à jour le champ MTP_ID des formulaires groupés après la
	// modification du champ MTT_ID
	$(document).on("change", "#id_MTT_ID", function() {
		$.ajax({
			data: $("#tmat_form").serialize(),
			dataType: "html",
			success: function(data) {
				$('select[id^="id_tdec_set-"][id$="-MTP_ID"]').each(
					function() {
						let before = $(this);
						let after = $("#" + before.attr("id"), $(data));
						before.replaceWith(after);
					}
				);
			},
			type: "POST"
		});
	});

})(jQuery);