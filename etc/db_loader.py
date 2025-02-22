import sqlite3
import csv
import re

con = sqlite3.connect("nfl-five.db")

cur = con.cursor()

cur.execute("CREATE TABLE sets (set_id INTEGER PRIMARY KEY ASC, set_short_name TEXT, set_name TEXT, set_year_released TEXT, set_icon TEXT, set_card_count INTEGER)")
con.commit()
cur.execute("INSERT INTO sets (set_short_name, set_name, set_year_released, set_card_count) values ('19', 'NFL Five 2019', '2019', 331)")
cur.execute("INSERT INTO sets (set_short_name, set_name, set_year_released, set_card_count) values ('20', 'NFL Five 2020', '2020', 307)")
cur.execute("INSERT INTO sets (set_short_name, set_name, set_year_released, set_card_count) values ('21', 'NFL Five 2021', '2021', 326)")
cur.execute("INSERT INTO sets (set_short_name, set_name, set_year_released, set_card_count) values ('22', 'NFL Five 2022', '2022', 259)")
cur.execute("INSERT INTO sets (set_short_name, set_name, set_year_released, set_card_count) values ('MCI', 'NFL Five Minicamp Collection I', '2024', 5)")
con.commit()

cur.execute("CREATE TABLE card_types (card_type_id INTEGER PRIMARY KEY ASC, card_type TEXT)")
con.commit()
cur.execute("INSERT INTO card_types (card_type) values ('Player')")
cur.execute("INSERT INTO card_types (card_type) values ('Play')")
cur.execute("INSERT INTO card_types (card_type) values ('Action')")
cur.execute("INSERT INTO card_types (card_type) values ('Synergy')")
cur.execute("INSERT INTO card_types (card_type) values ('Gridiron')")
con.commit()

cur.execute("CREATE TABLE rarity (rarity_id INTEGER PRIMARY KEY ASC, rarity_short_name TEXT, rarity TEXT)")
con.commit()
cur.execute("INSERT INTO rarity (rarity_short_name, rarity) values ('C', 'Common')")
cur.execute("INSERT INTO rarity (rarity_short_name, rarity) values ('U', 'Uncommon')")
cur.execute("INSERT INTO rarity (rarity_short_name, rarity) values ('R', 'Rare')")
cur.execute("INSERT INTO rarity (rarity_short_name, rarity) values ('E', 'Epic')")
cur.execute("INSERT INTO rarity (rarity_short_name, rarity) values ('L', 'Legendary')")
cur.execute("INSERT INTO rarity (rarity_short_name, rarity) values ('RK', 'Rookie')")
cur.execute("INSERT INTO rarity (rarity_short_name, rarity) values ('P', 'Promo')")
cur.execute("INSERT INTO rarity (rarity_short_name, rarity) values ('S', 'Special')")
cur.execute("INSERT INTO rarity (rarity_short_name, rarity) values ('X', 'X-tra')")
con.commit()

cur.execute("CREATE TABLE cards (id INTEGER PRIMARY KEY ASC, card_set_number TEXT, card_name TEXT, card_type_id INTEGER, rarity_id INTEGER, rating INTEGER, team TEXT, position TEXT, side TEXT, ability TEXT, special_text TEXT, strength TEXT, time_units TEXT, offensive_play TEXT, defensive_play TEXT, card_sub_type TEXT, card_effect TEXT, card_timing TEXT, set_id INTEGER, FOREIGN KEY(card_type_id) REFERENCES card_types(id), FOREIGN KEY(card_type_id) REFERENCES card_types(id), FOREIGN KEY(rarity_id) REFERENCES rarity(id), FOREIGN KEY(set_id) REFERENCES sets(id))")
con.commit()

rarity_pattern = re.compile(r"^([a-zA-Z]{1,2})")

#Parse the data

set_postfixes = ['2019', '2020', '2021', '2022', 'Minicamp Collection I']

for set_postfix in set_postfixes:
    count = 0
    with open(f'{set_postfix}.csv', newline='') as csvfile:
        file_reader = csv.reader(csvfile, delimiter=',')
        for row in file_reader:
            count = count + 1
            print(f"{count}: {row}")
            the_card_set_number = row[0]
            the_card_name = row[1]
            the_card_type = row[2]
            matches = rarity_pattern.match(the_card_set_number)
            the_card_rarity = matches.group()
            the_rating = row[3] #Player rating (player card only)
            the_team = row[4] #NFL Team player is on (player card only)
            the_position = row[5] #QB/RB/DB etc (player card only)
            the_side = row[6] #Offense / Defense (player card only)
            the_ability = row[7] #Player card ability (player card only)
            the_special_text = row[8] #Superstar / Legend (player card only)
            the_strength = row[9] #Strength of play
            the_time_units = row[10] #time units for play
            the_offensive_play = row[11] #play cards only
            the_defensive_play = row[12] #play cards only
            the_card_sub_type = row[13] #Action Cards // Gridiron Cards
            the_card_effect = row[14] #Action / Gridiron / Synergy
            the_card_timing = row[15] #Action / Gridiron / Synergy
            the_card_set = f'NFL Five {set_postfix}'

            cur.execute("INSERT INTO cards (card_set_number, card_name, card_type_id, rarity_id, rating, team, position, side, ability, special_text, strength, time_units, offensive_play, defensive_play, card_sub_type, card_effect, card_timing, set_id) VALUES (?, ?, (SELECT card_type_id FROM card_types WHERE card_type = ?), (SELECT rarity_id FROM rarity where rarity_short_name = ?), ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, (SELECT set_id FROM sets where set_name = ?))", [the_card_set_number, the_card_name, the_card_type, the_card_rarity, the_rating, the_team, the_position, the_side, the_ability, the_special_text, the_strength, the_time_units, the_offensive_play, the_defensive_play, the_card_sub_type, the_card_effect, the_card_timing, the_card_set])

con.commit()
