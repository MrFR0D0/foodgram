import data from '../data.json';

class Api {
  constructor() {
    this._data = data;
    this._usersById = this._data.users.reduce((acc, user) => {
      acc[user.id] = user;
      return acc;
    }, {});
    this._tagsById = this._data.tags.reduce((acc, tag) => {
      acc[tag.id] = tag;
      return acc;
    }, {});
  }

  // Helper to simulate network delay
  simulateDelay(data) {
    return new Promise(resolve => {
      setTimeout(() => resolve(data), 200); // 200ms delay
    });
  }

  // Helper to enrich recipe data
  enrichRecipe(recipe) {
    return {
      ...recipe,
      author: this._usersById[recipe.author] || null,
      tags: recipe.tags.map(tagId => this._tagsById[tagId]).filter(Boolean),
    };
  }

  // Mocked authentication methods
  signin({ email, password }) {
    console.log('signin called, but is disabled in static mode.');
    return Promise.reject({ error: 'Authentication is disabled.' });
  }

  signout() {
    console.log('signout called, but is disabled in static mode.');
    return Promise.resolve();
  }

  signup({ email, password, username, first_name, last_name }) {
    console.log('signup called, but is disabled in static mode.');
    return Promise.reject({ error: 'Registration is disabled.' });
  }

  getUserData() {
    console.log('getUserData called, but is disabled in static mode.');
    return Promise.resolve(null);
  }

  changePassword({ current_password, new_password }) {
    console.log('changePassword called, but is disabled in static mode.');
    return Promise.reject({ error: 'Password change is disabled.' });
  }

  // Recipes
  getRecipes({
    page = 1,
    limit = 6,
    author,
    tags,
  } = {}) {
    let recipes = [...this._data.recipes];

    if (author) {
      recipes = recipes.filter(recipe => recipe.author === Number(author));
    }

    if (tags && tags.length > 0) {
        const selectedTags = tags.filter(t => t.value).map(t => t.slug);
        if (selectedTags.length > 0) {
            const tagIds = this._data.tags
                .filter(tag => selectedTags.includes(tag.slug))
                .map(tag => tag.id);
            recipes = recipes.filter(recipe => 
                recipe.tags.some(tagId => tagIds.includes(tagId))
            );
        }
    }

    const enrichedRecipes = recipes.map(this.enrichRecipe.bind(this));

    // Pagination
    const startIndex = (page - 1) * limit;
    const paginatedRecipes = enrichedRecipes.slice(startIndex, startIndex + limit);

    return this.simulateDelay({
      count: enrichedRecipes.length,
      results: paginatedRecipes,
    });
  }

  getRecipe({ recipe_id }) {
    const recipe = this._data.recipes.find(r => r.id === Number(recipe_id));
    if (recipe) {
      return this.simulateDelay(this.enrichRecipe(recipe));
    } else {
      return Promise.reject({ error: 'Recipe not found.' });
    }
  }

  // Users
  getUser({ id }) {
    const user = this._data.users.find(u => u.id === Number(id));
    if (user) {
      return this.simulateDelay(user);
    } else {
      return Promise.reject({ error: 'User not found.' });
    }
  }

  // Ingredients
  getIngredients({ name }) {
    let ingredients = [...this._data.ingredients];
    if (name) {
      ingredients = ingredients.filter(i => i.name.toLowerCase().includes(name.toLowerCase()));
    }
    return this.simulateDelay(ingredients);
  }

  // Tags
  getTags() {
    return this.simulateDelay(this._data.tags);
  }

  // Disabled actions
  createRecipe(args) { return Promise.reject({ error: 'Action disabled' }) }
  updateRecipe(args) { return Promise.reject({ error: 'Action disabled' }) }
  addToFavorites(args) { return Promise.reject({ error: 'Action disabled' }) }
  removeFromFavorites(args) { return Promise.reject({ error: 'Action disabled' }) }
  copyRecipeLink(args) { return Promise.reject({ error: 'Action disabled' }) }
  getSubscriptions(args) { return Promise.resolve({ results: [] }) } // Return empty for lists
  deleteSubscriptions(args) { return Promise.reject({ error: 'Action disabled' }) }
  subscribe(args) { return Promise.reject({ error: 'Action disabled' }) }
  addToOrders(args) { return Promise.reject({ error: 'Action disabled' }) }
  removeFromOrders(args) { return Promise.reject({ error: 'Action disabled' }) }
  deleteRecipe(args) { return Promise.reject({ error: 'Action disabled' }) }
  downloadFile(args) { return Promise.reject({ error: 'Action disabled' }) }
}

export default new Api();
