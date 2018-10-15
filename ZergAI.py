import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import LARVA, DRONE

class ZergAI(sc2.BotAI):
    async def on_step(self, iteration):
        await self.distribute_workers()
        await self.build_workers()

    async def build_workers(self):
        larvae = self.units(LARVA)
        if self.can_afford(DRONE) and larvae.exists:
            await self.do(larvae.random.train(DRONE))


run_game(maps.get("AbyssalReefLE"), [
    Bot(Race.Zerg, ZergAI()),
    Computer(Race.Terran, Difficulty.Easy)
], realtime=True)