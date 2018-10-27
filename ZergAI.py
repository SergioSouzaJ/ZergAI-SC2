import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import LARVA, DRONE, OVERLORD, HATCHERY, EXTRACTOR

class ZergAI(sc2.BotAI):
    async def on_step(self, iteration):
        await self.distribute_workers()
        await self.build_workers()
        await self.build_overlords()
        await self.expand()
        await self.build_extractors()
        await self.assign_workers_to_gas()

    async def build_workers(self):
        larvae = self.units(LARVA)
        if self.can_afford(DRONE) and larvae.exists:
            await self.do(larvae.random.train(DRONE))
    
    async def build_overlords(self):
        if self.supply_left < 4 and not self.already_pending(OVERLORD):
            larvae = self.units(LARVA)            
            if self.can_afford(OVERLORD) and larvae.exists:
                await self.do(larvae.random.train(OVERLORD))

    async def expand(self):
        if self.can_afford(HATCHERY):
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


run_game(maps.get("AbyssalReefLE"), [
    Bot(Race.Zerg, ZergAI()),
    Computer(Race.Terran, Difficulty.Easy)
], realtime=False)