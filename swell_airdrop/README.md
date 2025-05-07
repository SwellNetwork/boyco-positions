# swell airdrop to boyco x kodiak rsweth-weth lps

how to:

* `source .venv/bin/activate` to activate env
* copy `../src/enriched-boyco-positions/enriched_boyco_positions.csv` to `csvs/in/enriched_boyco_positions.csv`
* `uv run main.py` to run script

methodology:

* filter for market id `0x3ef317447bd10825f0a053565f8474a460cfb22cda414ea30b671e304f0691b6`
* distribute swell on `input_token_raw_amount` column. why this column is chosen
  * constant timeperiod - fixed 90 day lock for all users
  * assumed constant eth price feed - i.e WETH:rswETH = 1:1 thus price remains constant for all users
  * hence pro-rata distribution will be on input token amount 