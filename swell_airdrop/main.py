import pandas as pd
from loguru import logger
from decimal import Decimal, getcontext

# Set precision high enough to handle large numbers
getcontext().prec = 50

# CONSTANTS
# sourced from ../src/enriched-boyco-positions/enriched_boyco_positions.csv
df = pd.read_csv("csvs/in/enriched_boyco_positions.csv")
# https://berachain.royco.org/market/1/0/0x3ef317447bd10825f0a053565f8474a460cfb22cda414ea30b671e304f0691b6
RSWETH_KODIAK_MARKET_ID = '0x3ef317447bd10825f0a053565f8474a460cfb22cda414ea30b671e304f0691b6'
SWELL_AIRDROP_AMOUNT = 10_000_000
DECIMAL_ADJ = Decimal(f"1e18")
COL = 'input_token_raw_amount'

# filter for market
df['market_id'] = df['market_id'].str.lower()
df = df[df['market_id'] == RSWETH_KODIAK_MARKET_ID]

# logger.info("Address count: {}", df['account_address'].nunique())

logger.info("Starting airdrop process...")
logger.info("Dataframe shape: {}", df.shape)
# logger.info("Dataframe columns: {}", df.columns)

# select relevant columns
df = df[['account_address', COL]]

# convert numbers to high precision decimal
token_amount_wei = Decimal(SWELL_AIRDROP_AMOUNT) * DECIMAL_ADJ
df['amount_wei'] = df[COL].apply(lambda x: Decimal(str(x)))
total_points = df['amount_wei'].sum()

# calculate the amount of SWELL to distribute
df['swell_amount_wei'] = df['amount_wei'].apply(
    lambda x: (x / total_points * token_amount_wei).quantize(
        Decimal("1"), rounding="ROUND_DOWN"
    )
)
df = df.sort_values(by='swell_amount_wei', ascending=False)
sum_distributed_wei = Decimal(df['swell_amount_wei'].sum())

logger.info("Level 1 distribution done")
logger.info(f"Total SWELL distributed in wei: {sum_distributed_wei}")
logger.info(
    f"Total SWELL distributed in 18 decimals: {sum_distributed_wei / DECIMAL_ADJ}"
)

if sum_distributed_wei == token_amount_wei:
    logger.info("Level 1 distribution successful")
else:
    logger.info("Level 1 distribution failed")
    logger.info(f"Difference WEI: {token_amount_wei - sum_distributed_wei}")
    logger.info(
        f"Difference: {(token_amount_wei - sum_distributed_wei) / DECIMAL_ADJ}"
    )

    # level 2 distribution for excess wei
    excess_wei = token_amount_wei - sum_distributed_wei

    if excess_wei < 0:
        raise ValueError("Excess wei is negative. Check your calculations.")

    top_addresses = df.head(int(excess_wei))  # Get top addresses
    for index in top_addresses.index:
        df.at[index, 'swell_amount_wei'] += Decimal("1")

    sum_distributed_wei = df['swell_amount_wei'].sum()
    logger.info(
        f"After redistribution, TOTAL SWELL WEI DISTRIBUTED: {sum_distributed_wei}"
    )
    logger.info(
        f"After redistribution, TOTAL SWELL DISTRIBUTED: {sum_distributed_wei / DECIMAL_ADJ}"
    )
    logger.info(
        f"Difference after redistribution WEI: {token_amount_wei - sum_distributed_wei}"
    )
    logger.info(
        f"Difference after redistribution: {(token_amount_wei - sum_distributed_wei) / DECIMAL_ADJ}"
    )

df['swell_amount'] = df['swell_amount_wei']/ DECIMAL_ADJ

df.to_csv("csvs/out/boyco_airdrop.csv", index=False)
logger.info("Airdrop process completed.")
logger.info("Airdrop CSV saved to csvs/out/airdrop.csv")