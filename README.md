# aquagraph_arrows
Aquagraph visualization in arrows

Steps
- Save the credentials `clarify-credentials.json` in the main folder
- Run the script `python process_items.py`
  - In the script you can define how many items to retrieve by changing the variable `n_items`, the number of created batches by changing the variable `n_batches` and the number of (random) initial connections between batch and items via the variable `connect_one_in_each`.
- Copy the content of the output file `result.json` to arrows.app by copying it.

Dependencies
- `pydantic`
- `pyclarify`
- Python 3.9
