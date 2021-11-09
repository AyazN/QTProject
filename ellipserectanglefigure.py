class ellipseorrectangle():
    def __init__(self, startx, starty, posx, posy):
        if startx > posx:
            self.x = startx + (posx - startx)
            self.xside = (startx - posx) * 2
        elif startx < posx:
            self.x = startx - (posx - startx)
            self.xside = (posx - startx) * 2
        else:
            self.x = posx
            self.xside = 0
        self.y = posy
        if starty > posy:
            self.yside = (starty - posy) * 2
        elif starty < posy:
            self.y = starty - (posy - starty)
            self.yside = (posy - starty) * 2
        else:
            self.yside = 0

    def drawing(self):
        return [self.x, self.y, self.xside, self.yside]
