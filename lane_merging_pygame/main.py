import pygame as pg
import GloDec as gd

def run():
    pg.init()
    gd.screen = pg.display.set_mode((gd.WIDTH, gd.HEIGHT))
    gd.clock = pg.time.Clock()

    while gd.running and len(gd.vehicles) > 0:
    
        gd.screen.fill(gd.bg)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                gd.running = False

        keys = pg.key.get_pressed()
        if keys[pg.K_RIGHT]:
            gd.v1.turn(1)
        if keys[pg.K_LEFT]:
            gd.v1.turn(-1)
        if keys[pg.K_UP]:
            gd.v1.accelerate()
        if keys[pg.K_DOWN]:
            gd.v1.decelerate()

        if keys[pg.K_d]:
            gd.v2.turn(1)
        if keys[pg.K_a]:
            gd.v2.turn(-1)
        if keys[pg.K_w]:
            gd.v2.accelerate()
        if keys[pg.K_s]:
            gd.v2.decelerate()

        gd.v2.move(1)
        gd.v1.move(1)

        pg.draw.line(gd.screen,"white",(0, 250), (gd.screen.get_width(), 250), 1)
        pg.draw.line(gd.screen,"white",(0, 430), (3*gd.screen.get_width()/4, 430), 1)
        pg.draw.line(gd.screen,"white",(3*gd.screen.get_width()/4, 430), (5*gd.screen.get_width()/6, 340), 1)
        pg.draw.line(gd.screen,"white",(5*gd.screen.get_width()/6, 340), (gd.screen.get_width(), 340), 1)


        for v in gd.vehicles:
            if v.out_of_screen():
                print(f"{'red' if v is gd.v1 else 'blue'} car out in {v.timestamp} s")
                print(gd.vehicles)
                gd.vehicles.remove(v)
                print(gd.vehicles)


        gd.v1.draw()
        gd.v2.draw()

        # flip() the display to put your work on screen
        pg.display.flip()

        # limits FPS to 60
        # dt is delta time in seconds since last frame, used for framerate-
        # independent physics.
        gd.dt = gd.clock.tick(60) / 1000

        


    pg.quit()

run()