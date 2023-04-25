from ynet import extract_ynet
from i24 import extract_i24

import pandas as pd
import time
import os

if __name__ == '__main__':
    bulletsdf_ynet = extract_ynet()
    print(f"Bullets from ynet: {len(bulletsdf_ynet)}")

    bulletsdf_i24 = extract_i24()
    print(f"Bullets from i24: {len(bulletsdf_i24)}")

    bulletsdf = pd.concat([bulletsdf_ynet, bulletsdf_i24])
    bulletsdf = bulletsdf.reset_index(drop=True)
    print(f"Total bullets: {len(bulletsdf)}")

    # Save the dataframe to a csv file with name bullets DDMMYYYY.csv
    #
    path = f"bullets.csv"
    full_path = os.path.join(os.path.dirname(__file__), path)
    if not os.path.exists(full_path):
        bulletsdf = bulletsdf.sort_values(by=['datetime'], ascending=False)
        bulletsdf = bulletsdf.reset_index(drop=True)
        bulletsdf = bulletsdf.drop_duplicates(subset=['title'])
        bulletsdf.to_csv(path, index=False, encoding='utf-8-sig')
    else:
        complete_df = pd.read_csv(full_path, encoding='utf-8-sig')
        complete_df = pd.concat([complete_df, bulletsdf])

        # Remove duplicates by title
        complete_df = complete_df.drop_duplicates(subset=['title'])
        complete_df = complete_df.reset_index(drop=True)
        complete_df['datetime'] = complete_df['datetime'].astype(str)
        complete_df = complete_df.sort_values(by=['datetime'], ascending=False)
        complete_df.to_csv(path, index=False)

    print(f"Saved {len(bulletsdf)} bullets to {path}")
