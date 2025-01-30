def calc_water_goal(weight, activity, temp):
    water_goal = weight * 30 + (500*activity)/30 + 500
    if temp > 25:
        water_goal -= 1000
    return round(water_goal)

def calc_calorie_goal(weight, height, age):
    calorie_goal = 10 * weight + 6.25 * height - 5 * age
    return round(calorie_goal)

def calc_calorie_consumption(prod_cal_100g, gramms):
    return round((prod_cal_100g*gramms)/100)

def water_requierement(train_duration):
    return round((200*train_duration)/30)