from PythonClientAPI.libs.Game import PointUtils
from PythonClientAPI.libs.Game.Enums import *
from PythonClientAPI.libs.Game.Entities import *
from PythonClientAPI.libs.Game.World import *
#from PythonClientAPI.libs.Game import Weapon


class PlayerAI:
    def __init__(self):
        pass
    
    def do_move(self, world, enemy_units, friendly_units):        
        """
        What you said:
        This method will get called every turn; Your glorious AI code goes here.
        
        :param World world: The latest state of the world.
        :param list[EnemyUnit] enemy_units: An array of all 4 units on the enemy team. Their order won't change.
        :param list[FriendlyUnit] friendly_units: An array of all 4 units on your team. Their order won't change.
        
        What we say:
        We've defined a number of sub-methods that we will call in do_move. The priority of the sub-methods increases as you go down the list; so powerup_at_position is the highest priority and move_to_nearest enemy is the lowest priority. Try reading this code (do_move) from the bottom up; the comments will make more sense)
        """
        
        # SOME ABBREVIATIONS:
        # funit or f_unit = friendly_unit
        # eunit or e_unit = enemy_unit
        # cp = control point (or mainframe)
        
        
        # If none of the other things work, try moving towards an opponent. This is low prioirty, because we expect our opponents to move to us!!
        self.move_to_nearest_enemy(friendly_units, world, enemy_units)
        
        # If there's a powerup or cp that's nearer to us than it is to the enemy, grab that first.
        self.powerup_or_cp_if_nearer_than_enemy(friendly_units, world, enemy_units)
        
        # Also, if we're stalled for some reason (cannot shoot, cannot move), then try heading to the nearest powerup
        self.powerup_if_nothingtodo(friendly_units, world, enemy_units, ShotResult, MoveResult)
        
        # Let's say we're headed towards something (enemy, cp or powerup). If it turns out that we can snag another powerup without taking any extra steps along the way, then might as well grab it
        self.powerup_if_on_way(friendly_units, world, enemy_units)
        
        # So you're not in shooting range or on a powerup. Then head to a CP then to stack up points!
        self.move_to_nearest_cp(friendly_units, world)        
        
        # If you're in shooting range, shoot like your life depends on it!
        self.shoot_if_can(friendly_units, world, enemy_units, ShotResult)
        
        # If you're currently on a powerup, take it. Duh
        self.powerup_at_position(friendly_units, world,  WeaponType, PickupType)    
        
    
    
    def move_to_nearest_enemy(self, friendly_units, world, enemy_units):
        '''Each unit moves towards the enemy that's nearest to it'''
        for i in range(4):
            ipos = friendly_units[i].position
            lis = [0,0,0,0]
            for j in range(4):
                lis[j] = world.get_path_length(ipos,enemy_units[j].position)
                # lis[j] = distance from funit[i] to eunit[j]
                
            ind = lis.index(min(lis)) 
            # index of the nearest enemy unit
            print('move_to_nearest_enemy result*********************')
            print(friendly_units[i].move_to_destination(enemy_units[ind].position) )
            friendly_units[i].move_to_destination(enemy_units[ind].position) 


    
    def move_to_nearest_cp(self, friendly_units, world):
            '''Each unit moves towards the cp that's nearest to it that is NOT held by funit'''
            for i in range(4):
                ipos = friendly_units[i].position
                not_our_cps = []
                       
                x=0          
                for cp in world.control_points:
                    if cp.controlling_team != friendly_units[0].team:
                        not_our_cps.append(cp)
                        x=1
                        # populated the list with our control points
                dists = []
                if x==0:
                    return
                
                for cp in not_our_cps:
                    dists.append(world.get_path_length(ipos, cp.position))
                ind = dists.index(min(dists)) 
                # index of the nearest enemy unit
                print('move_to_nearest_cp result*************************')
                print(friendly_units[i].move_to_destination(not_our_cps[ind].position))
                friendly_units[i].move_to_destination(not_our_cps[ind].position) 
           
           
    
    def shoot_if_can(self, friendly_units, world, enemy_units, ShotResult):
        '''If a funit is within shooting range of an eunit, shoot it'''
        for i in range(4):
            for j in range(4): #Check every funit against every other eunit 
                #print(friendly_units[i].check_shot_against_enemy(enemy_units[j]))
                if friendly_units[i].check_shot_against_enemy(enemy_units[j]) == ShotResult.CAN_HIT_ENEMY:
                    friendly_units[i].shoot_at(enemy_units[j])
                
                
                
    def powerup_if_nothingtodo(self, friendly_units, world, enemy_units, ShotResult, MoveResult):
        '''If a funit cannot hit an eunit this turn, AND couldn't move in preferred direction in prev. turn, AND doesn't have a scatter gun, then move in the direction of the nearest powerup'''
        # Check every funit with every eunit
        for i in range(4):
            for j in range(4):
                #check if cannot shoot an eunit this turn
                if friendly_units[i].check_shot_against_enemy(enemy_units[j]) != ShotResult.CAN_HIT_ENEMY:
                    #check if preferred movement blocked this turn
                    if friendly_units[i].last_move_result in (MoveResult.BLOCKED_BY_FRIENDLY, MoveResult.BLOCKED_BY_ENEMY):
                        if friendly_units[i].current_weapon_type != WeaponType.SCATTER_GUN:
                        
                        
                            print('Gonna head to the nearest powerup ****************')
                            
                            '''Head to the nearest powerup'''
                            pickups = []
                            pickup_distances = []
                            x=0
                            #Populate the lists "pickups" and "pickup_distances"
                            for pickup in world.pickups:
                                x=1
                                pickups.append(pickup)
                                pickup_distances.append(world.get_path_length(friendly_units[i].position,pickup.position))
                            if x==0:
                                
                                return # This avoids an error if world.pickups was actually empty
                            
                            #find the index of the pickup that is closest to funit
                            ind = pickup_distances.index(min(pickup_distances)) 
                            #move towards the pickup with that index
                            friendly_units[i].move_to_destination(pickups[ind].position)
                        
            print(friendly_units[i].last_move_result)
            
            
            
    def powerup_at_position(self, friendly_units, world, WeaponType, PickupType):
        '''If a funit is on top of a better powerup than it already has, then pick it up. 
        Best to worst is Scatter gun, rail gun sniper, laser rifle, blaster
        Should always pickup shield and/or health packs as these don't replace weapon'''
        for i in range(4):
            #friendly_units[i].pickup_item_at_position()
            
            print(friendly_units[i].current_weapon_type)
            if world.get_pickup_at_position(friendly_units[i].position) in (PickupType.SHIELD, PickupType.REPAIR_KIT):
                friendly_units[i].pickup_item_at_position()
            elif friendly_units[i].current_weapon_type == WeaponType.SCATTER_GUN:
                print('didnt pick up a weapon cuz I had a scatter gun bruh')
                continue
            else:
                friendly_units[i].pickup_item_at_position()
            print(friendly_units[i].pickup_item_at_position())  
            
            
            
    def powerup_or_cp_if_nearer_than_enemy(self, friendly_units, world, enemy_units):
        '''If dist to item < dist from enemy to item, then go grab that item'''
        for i in range(4):
            for j in range(4):
               
                for pickup in world.pickups: #first priority is to get to pickup
                    if world.get_path_length(friendly_units[i].position, pickup.position)+3 < world.get_path_length(enemy_units[j].position, pickup.position):
                        friendly_units[i].move_to_destination(pickup.position)
                        
                        
            
    def powerup_if_on_way(self, friendly_units, world, enemy_units):
        ''' This funit is going for the item if dis(me,item)+ dis(item,enemy) <= dis(me,enemy)'''
        for i in range(4): #number of ally units
            pickuplis = [] #list of distance to pickups
            p_to_enemy_lis = [] #list of distance from pickups to enemies
            total_lis = [] #list of elemental addition of the two above
            ipos = friendly_units[i].position  # current position of ally
            lis = [0, 0, 0, 0]
            for j in range(4): #number of enemy units


                lis[j] = world.get_path_length(ipos, enemy_units[j].position)

            ind = lis.index(min(lis)) #get the index of minimum distanced enemy
            e_dist = lis[ind] #get the distance

            x=0
            for pickup in world.pickups:
                x=1
                pickuplis.append(world.get_path_length(ipos, pickup.position)) #list of distance to pickups
                p_to_enemy_lis.append(world.get_path_length(pickup.position,enemy_units[ind].position))
                # list of distance from pickups to enemy units
                total_lis.append(0)
            if x==0:
                return

            for k in range(0,len(pickuplis)):
                total_lis[k] = pickuplis[k] + p_to_enemy_lis[k] #add the two distances

            ind_min = total_lis.index(min(total_lis)) #get the minimum distance's index
           

            if e_dist +2>= total_lis[ind_min]: #if getting item requires no extra step, go for it
                friendly_units[i].move_to_destination(world.pickups[ind_min].position) #move to the item's location

