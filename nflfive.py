def generateUrl(the_card_number, the_card_type, the_card_set, the_card_special_text):
  the_card_image_url = ""
  #print(f"{the_card_number}-{the_card_type}-{the_card_set}")

  if the_card_set == "NFL Five 2019":
    the_card_image_url = f"https://paninigames.com/wp-content/uploads/2019/08/{the_card_number.lower()}.jpg"

  elif the_card_set == "NFL Five 2020":
    if the_card_type == "Player":
      if the_card_number[:2].lower() == "rk":
        the_card_image_url = f"https://paninigames.com/wp-content/uploads/2020/08/{the_card_number.lower()}_50855_1142f0_rookie_ccg.jpg"
      else:
        the_card_image_url = f"https://paninigames.com/wp-content/uploads/2020/08/{the_card_number.lower()}_50854_1142f0_player_ccg.jpg"
    elif the_card_type == "Play":
      the_card_image_url = f"https://paninigames.com/wp-content/uploads/2020/08/{the_card_number.lower()}_50859_1142f0_play_ccg.jpg"
    elif the_card_type == "Action":
      the_card_image_url = f"https://paninigames.com/wp-content/uploads/2020/08/{the_card_number.lower()}_50856_1142f0_actiondefe_ccg.jpg"

  elif the_card_set == "NFL Five 2021":
    if the_card_type == "Player":
      if the_card_number[:2].lower() == "rk":
        the_card_image_url = f"https://paninigames.com/wp-content/uploads/2021/07/{the_card_number.lower()}_en_64706_1269f0_rookie.jpg"
      elif the_card_special_text == 'Superstar':
        the_card_image_url = f"https://paninigames.com/wp-content/uploads/2021/07/{the_card_number.lower()}_en_64835_1269f0_superscard.jpg"
      else:
        the_card_image_url = f"https://paninigames.com/wp-content/uploads/2021/07/{the_card_number.lower()}_en_64705_1269f0_player.jpg"
    elif the_card_type == "Play":
      the_card_image_url = f"https://paninigames.com/wp-content/uploads/2021/07/{the_card_number.lower()}_en_64710_1269f0_play.jpg"
    elif the_card_type == "Action":
      the_card_image_url = f"https://paninigames.com/wp-content/uploads/2021/07/{the_card_number.lower()}_en_64707_1269f0_actiondefe.jpg"
    elif the_card_type == "Gridiron":
      the_card_image_url = f"https://paninigames.com/wp-content/uploads/2021/07/{the_card_number.lower()}_en_64832_1269f0_gridircard.jpg"
    elif the_card_type == "Synergy":
      the_card_image_url = f"https://paninigames.com/wp-content/uploads/2021/07/{the_card_number.lower()}_en_64833_1269f0_synergcard.jpg"

  elif the_card_set == "NFL Five 2022":
    the_card_image_url = f"https://paninigames.com/wp-content/uploads/2022/07/{the_card_number.lower()}.jpg"

  elif the_card_set == "NFL Five Minicamp Collection I":
    if the_card_number == 'X1':
      the_card_image_url = f"https://paninigames.com/wp-content/uploads/2024/03/synergycard2.png"
    elif the_card_number == 'X2':
      the_card_image_url = f"https://paninigames.com/wp-content/uploads/2024/04/4.png"
    elif the_card_number == 'X3':
      the_card_image_url = f"https://paninigames.com/wp-content/uploads/2024/04/3.png"
    elif the_card_number == 'X4':
      the_card_image_url = f"https://paninigames.com/wp-content/uploads/2024/04/2.png"
    elif the_card_number == 'X5':
      the_card_image_url = f"https://paninigames.com/wp-content/uploads/2024/04/5.png"

  return the_card_image_url
