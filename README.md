# IPOWBDB

### Recommended workflow

It is recommended to use:

- **VS Code** for editing the notebook locally
- **GitHub** for storing and versioning the notebook
- **Google Colab** for running the notebook in the cloud

### Notes

- Keep the notebook as self-contained as possible
- Algorithms implementations and anything that could be extracted to Python code put in `/src`. In notebook `start.ipnyb` the repo is cloned for running on Google Colab and for the local development this part is skipped.
- Any required packages for the Python code put inside the `requirements.txt`, and anything Jupyter NB dependant put inside some notebook's top cell.
- Treat GitHub as the main place for sharing and syncing changes