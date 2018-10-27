import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import LARVA, DRONE, OVERLORD, HATCHERY, EXTRACTOR, \
    SPAWNINGPOOL, ROACHWARREN, ROACH, RAVAGER, EFFECT_CORROSIVEBILE, AbilityId
import random

class ZergAI(sc2.BotAI):

    async def on_step(self, iteration):
        await self.distribute_workers()
        await self.build_workers()
        await self.build_overlords()
        await self.expand()
        await self.build_extractors()
        await self.assign_workers_to_gas()
        await self.offensive_forces_buildings()
        await self.build_offensive_forces()
        await self.evolve_roach()
        await self.attack()

    async def build_workers(self):
        larvae = self.units(LARVA)
        if self.can_afford(DRONE) and larvae.exists and self.units(DRONE).amount < 36:
            await self.do(larvae.random.train(DRONE))
    
    async def build_overlords(self):
        if self.supply_left < 6 and not self.already_pending(OVERLORD):
            larvae = self.units(LARVA)            
            if self.can_afford(OVERLORD) and larvae.exists:
                await self.do(larvae.random.train(OVERLORD))

    async def expand(self):
        if self.units(HATCHERY).amount < 3 and self.can_afford(HATCHERY) and not self.already_pending(HATCHERY):
            await self.expand_now()
    
    async def build_extractors(self):
        for hatchery in self.units(HATCHERY).ready:
            vespenes = self.state.vespene_geyser.closer_than(14, hatchery)
            for vespene in vespenes:
                if not self.can_afford(EXTRACTOR):
                    break
                worker = self.select_build_worker(vespene.position)
                if worker is None:
                    break
                if not self.units(EXTRACTOR).closer_than(1, vespene).exists:
                    await self.do(worker.build(EXTRACTOR, vespene))
    
    async def assign_workers_to_gas(self):
        for extractor in self.units(EXTRACTOR):
            if extractor.assigned_harvesters < extractor.ideal_harvesters:
                worker = self.workers.closer_than(20, extractor)
                if worker.exists:
                    await self.do(worker.random.gather(extractor))

    async def offensive_forces_buildings(self):
        if not (self.units(SPAWNINGPOOL).exists or self.already_pending(SPAWNINGPOOL)):
            if self.can_afford(SPAWNINGPOOL):
                hq = self.townhalls.first
                await self.build(SPAWNINGPOOL, near=hq)

        if not (self.units(ROACHWARREN).exists or self.already_pending(ROACHWARREN)):
                if self.units(SPAWNINGPOOL).ready.exists and self.can_afford(ROACHWARREN):
                    sp = self.units(SPAWNINGPOOL).first
                    await self.build(ROACHWARREN, near=sp)

    async def build_offensive_forces(self):
        larvae = self.units(LARVA)
        if larvae.exists:
            if self.units(SPAWNINGPOOL).ready.exists:
                if self.can_afford(ROACH) and self.supply_left > 0:
                    await self.do(larvae.random.train(ROACH))

    async def evolve_roach(self):
        roaches = self.units(ROACH)
        if roaches.exists:
            if self.can_afford(RAVAGER):
                await self.do(roaches.random.train(RAVAGER))

    def find_target(self, state):
        if len(self.known_enemy_units) > 0:
            return random.choice(self.known_enemy_units)
        elif len(self.known_enemy_structures) > 0:
            return random.choice(self.known_enemy_structures)
        else:
            return self.enemy_start_locations[0]

    async def attack(self):
        for r in self.units(RAVAGER).idle:
            abilities = await self.get_available_abilities(r)
            if AbilityId.EFFECT_CORROSIVEBILE in abilities:
                await self.do(r(EFFECT_CORROSIVEBILE, self.find_target(self.state).position ))

        if self.units(RAVAGER).amount > 20:
            for r in self.units(RAVAGER).idle:
                await self.do(r.attack(self.find_target(self.state) ))
        
        elif self.units(RAVAGER).amount > 3:
            if len(self.known_enemy_units) > 0:
                for r in self.units(RAVAGER).idle:
                    await self.do(r.attack(self.find_target(self.state) ))

run_game(maps.get("AbyssalReefLE"), [
    Bot(Race.Zerg, ZergAI()),
    Computer(Race.Terran, Difficulty.Medium)
], realtime=False)