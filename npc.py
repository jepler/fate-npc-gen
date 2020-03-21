#!/usr/bin/env python3
import argparse
import functools
import itertools
import json
import operator
import os
import random

import names

ranks = ["Average", "Fair", "Good", "Great", "Superb", "Fantastic", "Epic", "Legendary"]

def shuffled(seq):
    seq = list(seq)
    random.shuffle(seq)
    return seq

@functools.lru_cache(maxsize=None)
def json_resource(fn):
    fn = os.path.join(os.path.dirname(__file__), fn)
    with open(fn) as f:
        return json.load(f)

def json_resource_set(fn):
    return set(json_resource(fn))

def choose_from_json(fn):
    return random.choice(json_resource(fn))

def choose_from_json_keys(fn):
    return random.choice(json_resource(fn).keys())

def choose_from_json_values(fn):
    return random.choice(json_resource(fn).keys())


feats = json_resource('skills.json')
feats.update(json_resource('skills-elder.json'))

all_skills = set(feats.keys())
for skill in all_skills:
    feats[skill] = set(f"{feat} [{skill}]" for feat in feats[skill])

def skill_levels():
    for i in itertools.count(1):
        for j in range(i):
            yield j+1

def take(n, seq):
    for i, j in zip(range(n), seq):
        yield j

def skill_pyramid(n):
    return sorted(take(n, skill_levels()), reverse=True)

class PropertyGenerator:
    def __init__(self, maker, *, type=str, metavar="...", nargs='?'):
        self._maker = maker
        self._key = "_" + maker.__name__
        self._validate = None
        self.type = type
        self.metavar = metavar
        self.nargs = nargs
        self.__doc__ = maker.__doc__

    def validator(self, fn):
        self._validate = fn
        return self

    def __get__(self, obj, type=None):
        key = self._key
        try:
            return getattr(obj, key)
        except AttributeError:
            value = self._maker(obj)
            if self._validate:
                value = self._validate(obj, value)
            setattr(obj, key, value)
            return value

    def __set__(self, obj, value):
        if self._validate:
            value = self._validate(obj, value)
        setattr(obj, self._key, value)

    def __delete__(self, obj):
        delattr(obj, self._key)

def generated_property(fn=None, **kw):
    if callable(fn):
        return PropertyGenerator(fn)
    def _inner(fn):
        return PropertyGenerator(fn, **kw)
    return _inner

class FateNPC:
    def __init__(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)
        
    @generated_property
    def name(self):
        return names.get_full_name()

    @generated_property(type=int)
    def skill_cap(self):
        return 4

    @generated_property(nargs='*')
    def skills(self):
        # Filled out by validator
        return []

    @skills.validator
    def skills(self, value):
        skills = set(value)
        if len(skills) != len(value):
            raise ValueError("duplicated skills")
        nskills = self.skill_cap * (self.skill_cap + 1) // 2
        if len(value) < nskills:
            other_skills = shuffled(all_skills - skills)
            value.extend(other_skills[:nskills - len(value)])
        return value

    @generated_property(type=int)
    def num_stunts(self):
        return self.skill_cap - 1

    @generated_property(nargs='*')
    def stunts(self):
        # Filled out by validator
        return []

    @stunts.validator
    def stunts(self, value):
        # When undefined, the first stunt is chosen from the top skill,
        # the second stunt from the top two skills, and so on.
        stunts = set(value)
        if len(stunts) != len(value):
            raise ValueError("duplicated stunts")
        skills_with_stunts = [i for i in self.skills if i in feats]
        while len(value) < self.num_stunts:
            choose_from_skills = skills_with_stunts[:1+len(value)]
            other_stunts = shuffled(functools.reduce(operator.__or__,
                (feats.get(sk, set()) for sk in choose_from_skills))-stunts)
            stunt = random.choice(other_stunts)
            value.append(stunt)
            stunts.add(stunt)
        return value

    @generated_property
    def high_concept(self):
        return choose_from_json('high-concepts.json')

    @generated_property
    def motto(self):
        return choose_from_json('mottos.json')

    @generated_property
    def advantage(self):
        return choose_from_json('advantages.json')

    @generated_property
    def trouble(self):
        return choose_from_json('troubles.json')

    @generated_property
    def disposition(self):
        return choose_from_json('dispositions.json')

    @generated_property
    def gear(self):
        return choose_from_json('gear.json')

    def print(self):
        print(self.name)
        print(f' "{self.motto}"')
        print()
        print(' High Concept:', self.high_concept)
        print(' Advantage:   ', self.advantage)
        print(' Trouble:     ', self.trouble)
        print(' Disposition: ', self.disposition)

        old_level = None
        for level, skill in zip(skill_pyramid(len(self.skills)), self.skills):
            if level != old_level:
                print(f"\n{ranks[level]:7} {level:+2} | ", end="")
                old_level = level
            print(f" {skill:12}", end="")
        print("\n")

        for stunt in self.stunts:
            print(stunt)
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate a Fate NPC')
    for k, v in FateNPC.__dict__.items():
        if isinstance(v, PropertyGenerator):
            parser.add_argument("--" + k,
                metavar=v.metavar,
                type=v.type,
                nargs=v.nargs,
                help=v.__doc__)
    args = parser.parse_args()
    npc = FateNPC()
    for k, v in args.__dict__.items():
        if v is not None:
            setattr(npc, k, v)
    npc.print()

