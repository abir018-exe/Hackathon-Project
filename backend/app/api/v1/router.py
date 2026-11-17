from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, teams, projects, scanner, intelligence, stabilization, demo, risk, testing, demo_script, activity, notifications, reports

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(teams.router, prefix="/teams", tags=["Teams"])
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])
api_router.include_router(scanner.router, prefix="/scanner", tags=["Scanner"])
api_router.include_router(intelligence.router, prefix="/intelligence", tags=["Intelligence"])
api_router.include_router(stabilization.router, prefix="/stabilization", tags=["Stabilization"])
api_router.include_router(demo.router, prefix="/demo", tags=["Demo Mode"])
api_router.include_router(risk.router, prefix="/risk", tags=["Risk Monitor"])
api_router.include_router(testing.router, prefix="/testing", tags=["Testing"])
api_router.include_router(demo_script.router, prefix="/demo-script", tags=["Demo Script"])
api_router.include_router(activity.router, prefix="/activity", tags=["Activity"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])