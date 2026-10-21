# Original 2011 service files

The `src/` directories contain the later package-ready versions recovered from
the 2015 `metactf` repository. The `original-2011/` directories preserve files
from the original iCTF 2011 service tree when their contents are not present
anywhere in the corresponding archived challenge.

These files were recovered from `ictf_2011/Services/` in `ictf_2011.7z`
(SHA-256 `9b08b1c1da0ee71445f5cd3d8ffe85038442adfa4adf53ba1b59888f99c1e27e`).
Their original directory structure is retained beneath each service. The
snapshot adds missing checkers, exploit helpers, SQL setup files, the eGoats
test suite, and original event-time revisions of several service files. The
shared `Services/update.sh` is under
`../infrastructure/original-2011-services/`.

The import contains 47 files across eight services. Nothing was needed for
`muleadmin` or `muleuser` because their source-like files already had exact
matches in the archive. Files already present byte-for-byte were not copied.

Excluded material includes `.svn` metadata, runtime state, databases, logs,
compiled files, large service data, and two generated Rails asset bundles.
