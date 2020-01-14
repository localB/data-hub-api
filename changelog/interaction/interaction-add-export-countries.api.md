Interactions API `/v3/interaction` now allows to specify if there was a discussion of countries during the interaction and add one or more export countries along with their status.

`were_countries_discussed` is a nullable boolean field.

`export_countries` field is of type `InteractionExportCountry` and takes a list of `country` and `status` combinations where `country` is of type `Country` and `status` is a choice of `Not interested`, `Currently exporting to` or `Future country of interest`.

* Above details are only valid for non-investment themed interactions. Hence `were_countries_discussed` is mandatory field for both `export` and `other` themed interactions.
* At least one country/status combination is mandatory if `were_countries_discussed` is set to True