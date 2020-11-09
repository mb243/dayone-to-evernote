# Day One 2 JSON to Evernote Importer

Import Day One 2 JSON exports to Evernote

Utilizes the [Evernote Python3 SDK](https://github.com/evernote/evernote-sdk-python3)

**NOTES**: 

- This was put together as a one-off script for my own use. I'm sharing it in case anyone else finds it helpful, but this may or may not be maintained at any point in the future.
- Markdown is converted to HTML by the `markdown` library. It does a pretty good job overall, but the output may not perfectly match original Day One entries.
- Original datetime stamps of entries are preserved
- Attachments are not preserved.

### Prerequisites 

- Python3
- The [Evernote Python3 SDK](https://github.com/evernote/evernote-sdk-python3)
- Additional required Python3 libraries

**One** of the following:
- An Evernote [dev token](https://dev.evernote.com/doc/articles/dev_tokens.php) **on Production**, OR
- An Evernote [OAuth application key](https://dev.evernote.com/doc/articles/authentication.php) **which has been approved for Production use**.

### Usage

This code is written to use OAuth for authentication. Using a dev token will simplify the authentication flow, but you will need to edit the code to use `get_client_by_dev_token` instead of `get_client_by_access_token`. 

- Export all Day One notes to a JSON export
- Unzip the exported zip file
- Edit `json_path` to point to the unzipped path, making sure that `Journal.json` is within that path
- Edit the code to add your authentication secrets
- Run it.
