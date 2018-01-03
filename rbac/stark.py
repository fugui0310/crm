from stark.service import router
from . import models
class UserConfig(router.StarkConfig):
    list_display = ['id','username','email']
    edit_link = ['username']
router.site.register(models.User,UserConfig)


class RoleConfig(router.StarkConfig):
    list_display = ['id','title',]
    edit_link = ['title']

router.site.register(models.Role,RoleConfig)




class PermissionConfig(router.StarkConfig):
    list_display = ['id','title','url','menu_gp','code']
router.site.register(models.Permission,PermissionConfig)




class GroupConfig(router.StarkConfig):
    list_display = ['id','caption','menu']
    edit_link = ['caption']
router.site.register(models.Group,GroupConfig)


class MenuConfig(router.StarkConfig):
    list_display = ['id','title']
    edit_link = ['title']
router.site.register(models.Menu,MenuConfig)