from module.sequence import SequencePath
from math import sqrt, dist
from pygame import Vector2

class PurePursuitSimulation:
    def __init__(self):
        pass

    def simulate_path(self, item: SequencePath) -> list[float, float]:
        """
        Uses pure pursuit to simulate the ideal of a robot along the entirety of 
        a given self.path, given that the robot starts at index 0.
        """
        self.path = item.curve.get_points()
        self.last_found_point = 0

        if 'look_ahead_dist' in item.custom_args:
            self.look_ahead_distance = item.custom_args['look_ahead_dist']['value'][1]
        else:
            self.look_ahead_distance = item.format['arguments']['look_ahead_dist']['value'][1]

        pos = Vector2(self.path[0])
        pos_list = []
        self.path_complete = False
        print("\n" + "#"*100)
        prev_msg = ""

        while not self.path_complete:
            solution = self.goal_point_search(pos)
            pos.move_towards_ip(solution, 20)

            pos_list.append(pos.copy())

            msg = f"calculating {pos} target {solution} end {self.path[-1]} lfp {self.last_found_point}"
            if msg != prev_msg:
                print(msg)
                prev_msg = msg
        
        return pos_list
        
    def goal_point_search(self, current_pos):
        start_point = self.last_found_point
        goal = self.path[self.last_found_point+1][:2]
        for i in range(start_point, len(self.path)-1):
            # convient variables
            h, k = current_pos
            point1 = self.path[i][:2]
            point2 = self.path[i+1][:2]
            ax, ay = point1[:2]
            bx, by = point2[:2]
            
            if (bx - ax) == 0:
                return goal
            m = (by - ay) / (bx - ax) # slope of line between point a and b
            b = m*(-ax) + ay # y-intercept of line
            r = self.look_ahead_distance
            # quadratic terms
            A = (m*m) + 1
            B = (2*m*(b-k)-(2*h))
            C = ((h*h) + ((b-k)*(b-k)) - (r*r))

            discriminant = (B*B) - (4*A*C)

            # one or more solutions exist
            # if positive, 2 solutions
            # if zero, 1 solution
            if discriminant >= 0:
                sol1_x = (-B + sqrt(discriminant)) / (2*A)
                sol1_y = m*sol1_x + b

                sol2_x = (-B - sqrt(discriminant)) / (2*A)
                sol2_y = m*sol2_x + b

                sol1 = (sol1_x, sol1_y)
                sol2 = (sol2_x, sol2_y)

                minX, minY = min(ax, bx), min(ay, by)
                maxX, maxY = max(ax, bx), max(ay, by)
                # general check to see if either point is on the line 
                if ((minX < sol1_x < maxX) and (minY < sol1_y < maxY)) or ((minX < sol2_x < maxX) and (minY < sol2_y < maxY)):

                    # both solutions are within bounds, so we need to compare and decide which is better
                    # choose based on distance to pt2
                    sol1_distance = dist(sol1, point2)
                    sol2_distance = dist(sol2, point2)

                    if ((minX < sol1_x < maxX) and (minY < sol1_y < maxY)) and ((minX < sol2_x < maxX) and (minY < sol2_y < maxY)):

                        if sol1_distance < sol2_distance:
                            goal = sol1
                        else:
                            goal = sol2
                    else:
                        if (minX < sol1_x < maxX) and (minY < sol1_y < maxY):
                            # solution 1 is within bounds
                            goal = sol1
                        else:
                            goal = sol2
                    

                # if the robot is within look_ahead_distance to the last point in the self.path,
                # we set our goal to that
                if dist(current_pos, self.path[len(self.path)-1][:2]) < self.look_ahead_distance:
                    goal = self.path[len(self.path)-1]
                else:
                    # update self.last_found_point
                    # only keep the goal if the goal point is closer to the target than our robot
                    if dist(goal, self.path[self.last_found_point+1][:2]) < dist(current_pos, self.path[self.last_found_point+1][:2]):
                        # found point is closer to the target than we are, so we keep it
                        goal = goal
                    else:
                        self.last_found_point = i

                if dist(current_pos, self.path[-1][:2]) < 50:
                    self.path_complete = True
            
            elif goal == ():
                # we didn't find any point on the line, so return the last found index
                goal = self.path[self.last_found_point][:2]
        
        return goal[:2]
