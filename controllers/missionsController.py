from pythonServer.errors.errors import EntityNotFound, UnableToCreate, UnableToGet, MissingAttribute, DuplicateEntity
from pythonServer.repositories.missionsRepository import get_missions

##if there are missions then add , else create schedule
class missionsController:
   async def create_mission(self, mission):
        if not mission:
            raise MissingAttribute("mission")
        existing_missions = await get_missions()
        if not existing_missions:
            return await create_schedule(mission)
        else:
            response = await create_mission(mission)
        return response

   async def create_schedule(self, schedule):
        if not schedule:
            raise MissingAttribute("schedule")
        existing_schedules = await get_missions()

        return schedule


