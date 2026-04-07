# IPOWBDB

## Recommended workflow

It is recommended to use:

- **VS Code** for editing the notebook locally
- **GitHub** for storing and versioning the notebook
- **Google Colab** for running the notebook in the cloud

## Usage (updated on 2026-03-25)

To add / remove dependencies and libraries:

```sh
uv add matplotlib     # add matplotlib
uv remove matplotlib  # remove matplotlib
```

To add / remove dependencies and libraries to the dev section (i.e. dependencies required for local development but not needed for running the notebook in Google Colab):

```sh
uv add --dev matplotlib
uv remove  --dev matplotlib
```

To generate the `requirements.txt` file from the non-dev dependencies:

```sh
uv export --no-hashes --no-dev --format requirements.txt --output-file requirements.txt
```

Then remember to commit the changes before synchronizing the notebook on Google Colab.

## Notes

- Keep the notebook as self-contained as possible
- Algorithms implementations and anything that could be extracted to Python code put in `/src`. In notebook `start.ipnyb` the repo is cloned for running on Google Colab and for the local development this part is skipped.
- Any required packages for the Python code put inside the `requirements.txt`, and anything Jupyter NB dependant put inside some notebook's top cell.
- Treat GitHub as the main place for sharing and syncing changes