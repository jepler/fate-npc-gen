import json
import random
import names

def pick_aspect(filename):
    with open(filename) as f:
        aspects = json.load(f)
    return random.choice(aspects)

print(names.get_full_name())
print("   High Concept: ", pick_aspect("high-concepts.json"))
print("   Motto:        ", pick_aspect("mottos.json"))
print("   Advantage:    ", pick_aspect("advantages.json"))
print("   Trouble:      ", pick_aspect("troubles.json"))
print("   Disposition:  ", pick_aspect("dispositions.json"))
print("   Gear:         ", pick_aspect("gear.json"))

nskills = random.randint(1,4) + random.randint(1,3) + random.randint(1,2) + 1
levels = []
mx = 0
j = 0
while len(levels) < nskills:
    levels.append(j)
    j = j + 1
    if j > mx:
        mx = mx + 1
        j = 0
levels.sort(reverse=True)

nstunts = random.randint(3, 5)

ranks = ["Average", "Fair", "Good", "Great"]

with open("skills.json") as f:
    skills_catalog = json.load(f)
with open("skills-elder.json") as f:
    skills_catalog.update(json.load(f))

k = list(skills_catalog.keys())
random.shuffle(k)
skills = k[:nskills]

old_rank = None
stunt_choices = []
for l, skill in zip(levels, skills):
    rank = ranks[l]
    if rank != old_rank:
        print(f"\n{rank:7} (+{1+l}) | ", end="")
        old_rank = rank
    stunts = [f"{stunt} [{skill}]" for stunt in skills_catalog[skill]]
    stunt_choices.extend(stunts * (1+l))
    print(f" {skill:12}", end="")
print("\n")

stunts = set()
while len(stunts) < nstunts:
    stunt = random.choice(stunt_choices)
    if stunt in stunts: continue
    print(stunt)
    stunts.add(stunt)
print()
print()
