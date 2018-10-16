import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import LARVA, DRONE, OVERLORD

class ZergAI(sc2.BotAI):
    async def on_step(self, iteration):
        await self.distribute_workers()
        await self.build_workers()
        await self.build_overlords()

    async def build_workers(self):
        larvae = self.units(LARVA)
        if self.can_afford(DRONE) and larvae.exists:
            await self.do(larvae.random.train(DRONE))
    
    async def build_overlords(self):
        if self.supply_left < 4 and not self.already_pending(OVERLORD):
            larvae = self.units(LARVA)            
            if self.can_afford(OVERLORD) and larvae.exists:
                await self.do(larvae.random.train(OVERLORD))


run_game(maps.get("AbyssalReefLE"), [
    Bot(Race.Zerg, ZergAI()),
    Computer(Race.Terran, Difficulty.Easy)
], realtime=True)