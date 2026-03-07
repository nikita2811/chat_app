# this file holds logic of user recommendation
COLD_CHAT_THRESHOLD = 5
COLD_FRIEND_THRESHOLD = 3

def is_cold_user(chat_count,friend_count):
    return chat_count < COLD_CHAT_THRESHOLD and friend_count < COLD_FRIEND_THRESHOLD                                
def interest_similarity(user,candidate):
    if not user or not candidate:
        return 0.0
    
    return len(user & candidate)/len(user | candidate)

def cold_user_recommendation(user,candidates):
    scores = []

    for c in candidates:
        score = interest_similarity(set(user["intrest"]),set(c["intrest"]))
        scores.append((c["id"], round(score, 3)))
        return sorted(scores, key=lambda x: x[1], reverse=True)


# warm user recommendation logic
def mutual_friend(user,candidate):
    return 1
def recommendations(user,candidates):
    result=[]
    for c in candidates:
        if is_cold_user:
            score = interest_similarity(user,c)
            result.append({c:score})
        else:
            mutual_friend(user,c)

