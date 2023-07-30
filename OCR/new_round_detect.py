    old_round = True
    index = 0
    cs_score = 0
    ss_score = 0   

        if old_round:
            winner = image[int(290 * height / 1440):int(325 * height / 1440), int(1100 * width / 2560):int(1460 * width / 2560)]
            results = reader.readtext(winner, allowlist='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-',
                                    paragraph=True, batch_size=8)
            winner_pr = ' '.join([result[1] for result in results])
            if len(winner_pr) >= 12:
                old_round = False
                distances = [Levenshtein.distance(winner_pr, target) for target in list]
                min_distance_index = distances.index(min(distances))
            
        else:
            index += 1
            if index == 160:
                if min_distance_index == 0:
                    ss_score += 1
                    old_round = True
                    player_alive = True
                else:
                    cs_score += 1 
                    old_round = True 
                    player_alive = True