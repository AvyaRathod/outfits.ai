package main

import (
	"log"
	"os"
	config "outfits/config"

	"outfits/routes"

	"github.com/gofiber/fiber/v2"
	"github.com/gofiber/fiber/v2/middleware/cors"
	"github.com/joho/godotenv"
)

func main() {
	err := godotenv.Load(".env")

	if err != nil {
		log.Fatalf("Error loading .env file")
	}

	config.ConnectDb()
	app := fiber.New()
	app.Use(cors.New(cors.Config{
		AllowOrigins:     "http://localhost:3000, http://54.164.84.100:3000",
		AllowCredentials: true,
	}))
	app.Get("/", func(c *fiber.Ctx) error {
		return c.SendString("Hello FIber")
	})

	api := app.Group("/api/v1")
	routes.SetUpUserRoutes(api)
	routes.SetUpClothingRoutes(api)
	port := os.Getenv("PORT")
	app.Listen(":" + port)

}
