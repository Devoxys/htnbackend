#!python3
from flask import Flask
import urllib.request
import json
import inflect
app = Flask(__name__)

p = inflect.engine()

# foodname -> string
# blacklist -> comma seperated list of strings e.g. "apple,banna,orange"

APP_ID_SEARCH = "08c67c26"
APP_KEY_SEARCH = "d22fafacab5449e1405a9937b7a0a7ba"
allergies = []

def find_health_lable(l):
    if l == "vegetarian":
        return "Vegetarian"
    if l == "vegan":
        return "Vegan"
    if l == "peanut":
        return "Peanut-Free"
    if l == "tree-nut":
        return "Tree-Nut-Free"
    if l == "alcohol":
        return "Alcohol-Free"


def confidence(res):
    conf = dict()
    # Give user confidence level
    for i in res.keys():
        if res[i] <= 0.1:
            conf[i] = "Very Unlikely"
        elif res[i] <= 0.3:
            conf[i] = "Unlikely"
        elif res[i] <= 0.6:
            conf[i] = "Moderate Chance"
        elif res[i] <= 0.8:
            conf[i] = "Likely"
        else:
            conf[i] = "Very Likely"
    return conf


@app.route('/<foodname>')
def f(foodname):
    blacklist = allergies[-1]
    bad = blacklist.split(",")
    for x in bad:  # parse blacklist
        x = x.lower()
        x = p.singular_noun(x)
    foodname = foodname.replace(" ", "%20")  # parse foodname
    print(bad)
    # Request list of ingredients for dish from Edamam API
    # change amount of results later maybe if need more precision
    url = "https://api.edamam.com/search?q="+foodname+"&app_id="+APP_ID_SEARCH+"&app_key=" + APP_KEY_SEARCH + "&to=100"
    print(url)
    contents = urllib.request.urlopen(url).read()
    ingredients = []
    contents = json.loads(contents)
    
    hits = contents["hits"]  # list of recipes

    # count appearances of blacklisted ingredients in recipes
    cnt = {}
    test = []
    res1 = dict()
    res2 = dict()

    labels = ["vegetarian", "vegan", "peanut", "tree-nut", "alcohol"]
    ltc = []
    for l in labels:
        if l in bad:
            ltc.append(l)
    print(ltc)
    # look through recipes and their ingredients
    for hit in hits:
        recipe = hit["recipe"]
        ingred = recipe["ingredients"]
        health = recipe["healthLabels"]


        # print(ingred)
        for x in ingred:
            # print(x["text"])
            ingredients.append(x["text"])

        for l in ltc:
            hl = find_health_lable(l)
            if hl in health:
                if l not in res1.keys():
                    res1[l] = 1
                else:
                    res1[l] += 1
    print(res1)
    for (k, v) in res1.items():
        if k == "vegetarian" or k == "vegan":
            res1[k] = v/100
        else:
            res1[k] = (100-v)/100
    print(res1)

    for l in ltc:
        if l in bad:
            bad.remove(l)
        print(bad)

    for i in bad:
        a = 0
        for j in ingredients:
            a += j.lower().count(i)
        
        cnt[i] = a
        print("count of "+i+" is "+str(a))
        test.append("count of "+i+" is "+str(a))

        res2[i] = a/100  # % chance that a blacklisted ingredient will be in dish given recipes (NOT VERY ACCURATE)

    conf1 = confidence(res1)
    print(conf1)
    conf2 = confidence(res2)
    print(conf2)
    # print(contents)
    conf2.update(conf1)
    return str(conf2)


@app.route('/updRestrictions/<string:newStr>')
def updRestrictions(newStr):
    print(newStr)
    allergies.append(newStr)
    return "allergies is now "+newStr


@app.route('/queryRestrictions')
def queryRestrictions():
    print("hello")
    print("returning "+allergies[-1])
    print(allergies[-1])
    return allergies[-1]


if __name__ == "__main__" :
    app.run(host='0.0.0.0', port = 42068, debug = True)