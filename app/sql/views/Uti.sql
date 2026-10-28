/*
==============================================================================
Crée une vue enrichissant les données de la table T_E_UTILISATEUR_UTI à l'aide
de colonnes calculées.
==============================================================================
*/
CREATE OR REPLACE VIEW "public"."V_UTI" AS
	SELECT
		UTI.id
			AS "UTI_ID",
		concat_ws(
			' ',
			nullif(initcap(trim(UTI.first_name)), ''),
			nullif(upper(trim(UTI.last_name)), '')
		)::CHARACTER VARYING(301)
			AS "UTI_NOM",
		upper(split_part(UTI.email, '@', 1))::CHARACTER VARYING(254)
			AS "UTI_UID"
	FROM "public"."T_E_UTILISATEUR_UTI" AS UTI;