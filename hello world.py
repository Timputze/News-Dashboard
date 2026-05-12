import turtle

# Set up the screen
screen = turtle.Screen()
screen.bgcolor("white")
screen.title("Smiley Face")

# Create a turtle object
smiley = turtle.Turtle()
smiley.speed(5)

# Draw the face (circle)
smiley.penup()
smiley.goto(0, -100)
smiley.pendown()
smiley.begin_fill()
smiley.fillcolor("yellow")
smiley.circle(100)
smiley.end_fill()

# Draw the left eye
smiley.penup()
smiley.goto(-35, 35)
smiley.pendown()
smiley.begin_fill()
smiley.fillcolor("black")
smiley.circle(10)
smiley.end_fill()

# Draw the right eye
smiley.penup()
smiley.goto(35, 35)
smiley.pendown()
smiley.begin_fill()
smiley.fillcolor("black")
smiley.circle(10)
smiley.end_fill()

# Draw the smile
smiley.penup()
smiley.goto(-50, -20)
smiley.setheading(-60)
smiley.pendown()
smiley.pensize(5)
smiley.circle(60, 120)

# Hide the turtle
smiley.hideturtle()

# Keep the window open
screen.mainloop()