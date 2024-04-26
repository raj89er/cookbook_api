## Cookbook CRUD App Design and Functionality

### Database Design (ERD)

#### Users Table
Stores user information for registration, authentication, and authorization. Manages user accounts within the app.

| Field             | Data Type        | Key                 |
|-------------------|------------------|---------------------|
| user_id           | INT              | Primary             |
| username          | TEXT(50)         | Unique, not null    |
| email             | TEXT(50)         | Unique              |
| password          | TEXT             |                     |
| token             | TEXT             |                     |
| token_expiration  | DATETIME         |                     |

#### Recipes Table
Contains details of recipes, including cook time, prep time, ingredients, directions, and tips.

| Field             | Data Type        | Key                 |
|-------------------|------------------|---------------------|
| recipe_id         | INT              | Primary             |
| title             | TEXT             | Not null            |
| cook_time         | INT              |                     |
| prep_time         | INT              |                     |
| tips              | TEXT             |                     |
| created_at        | DATETIME         |                     |
| user_id           | INT              | Foreign key (Users) |

#### Ingredients Table
Stores ingredient details for recipes, including quantity and units.

| Field             | Data Type        | Key                 |
|-------------------|------------------|---------------------|
| ingredient_id     | INT              | Primary             |
| name              | VARCHAR(100)     | Not null            |
| quantity          | FLOAT            |                     |
| units             | VARCHAR(20)      |                     |
| recipe_id         | INT              | Foreign key (Recipes)|

#### Directions Table
Stores step-by-step instructions for recipes.

| Field             | Data Type        | Key                 |
|-------------------|------------------|---------------------|
| direction_id      | INT              | Primary             |
| step_number       | INT              | Not null            |
| instruction       | TEXT             | Not null            |
| recipe_id         | INT              | Foreign key (Recipes)|

#### Favorites Table
Stores information about recipes marked as favorites by users.

| Field             | Data Type        | Key                 |
|-------------------|------------------|---------------------|
| user_id           | INT              | Primary, Foreign key (Users)|
| recipe_id         | INT              | Primary, Foreign key (Recipes)|
| is_fav            | BOOLEAN          |                     |



### API Routes and Endpoints

- [GET] : [/token]
    - tokens for everyone!
- [POST] - [/users]
    - create a new user
- [GET] - [/users/me]
    - info about the user
- [GET] - [/users/user_id]
    - methods=specific user.
- [PUT] - [/users/me]
    - update the user
- [DELETE] - [/users/me]
    - delete current user
---
- [GET] - [/recipes]
    - get all recipes
- [GET] - [/recipes/<recipe_id>]
    - get a specific recipe
- [POST] - [/recipes]
    - create a new recipe

#### Possible Routes....

[GET] /recipes: Retrieve a list of all recipes (no need to be logged in).
[GET] /recipes/<recipe_id>: Get details of a specific recipe by its ID.
[POST] /recipes: Create a new recipe (user needs to be logged in).
[PUT] /recipes/<recipe_id>: Update an existing recipe (the user has to be the author).
[DELETE] /recipes/<recipe_id>: Delete a recipe (the user has to be the author).

Additionally, we can create other routes regarding the User and Recipe Tables as follows:

[GET] /users/recipes: Retrieve all recipes created by the user.
[GET] /users/recipes/<recipe_id>: Get details of a specific recipe created by the user.
[PUT] /users/recipes/<recipe_id>: Update a recipe created by the user.
[DELETE] /users/recipes/<recipe_id>: Delete a recipe created by the user.

/ home page
/recipes
/recipes/<recipe_id> 

### Navbar and Pages
- **Navbar:**
  - Include links to the home page, recipes page, login page, and about us page for easy navigation.
  - Implement a search bar for users to search for specific recipes.
- **Home Page:**
  - Display a welcome message and brief introduction to the app.
  - Provide quick access to popular or featured recipes.
- **Recipes Page:**
  - Show a list or grid view of all available recipes.
  - Include sorting and filtering options (e.g., by category, cuisine, cooking time).
- **Recipe Details Page:**
  - When a recipe is clicked, navigate to a dedicated recipe details page.
  - Display recipe name, description, ingredients with quantities, directions, cook time, prep time, and other relevant details.
  - Include buttons to toggle ingredient visibility and mark ingredients as crossed out when used.

### Ingredient View and Quantity Multiplier
- **Ingredient View:**
  - Add buttons next to each ingredient to toggle visibility (show/hide) for easy tracking while cooking.
  - Use checkboxes or strike-through styling to visually indicate ingredients that have been used.
- **Quantity Multiplier:**
  - Include a dropdown or buttons for the user to select a multiplier (1x, 2x, 4x, 6x) to adjust ingredient quantities accordingly.
  - Update the displayed ingredient quantities dynamically based on the selected multiplier.

### Authentication and User Management
- **Login Page:**
  - Create a login page with forms for users to enter their credentials.
  - Implement authentication using JSON Web Tokens (JWT) for secure user sessions.
- **User Management:**
  - Allow registered users to create, edit, and delete their own recipes.
  - Implement role-based access control for admin privileges (e.g., managing all recipes, users).


start on flask
make the tables
use supabase
