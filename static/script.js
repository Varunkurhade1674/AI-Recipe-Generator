// AI Recipe Generator — Dashboard interactivity
// Handles: view switching, recipe generation, copy/save/download, history.

let currentRecipe = null;
let currentRecipeId = null;

document.addEventListener('DOMContentLoaded', () => {
  setupNavigation();
  setupRecipeForm();
  setupRecipeActions();
  setupHistoryOpeners();
});

// ---------------------------------------------------------------------
// Sidebar navigation
// ---------------------------------------------------------------------

function setupNavigation() {
  const navItems = document.querySelectorAll('.nav-item[data-view]');
  navItems.forEach((item) => {
    item.addEventListener('click', () => {
      navItems.forEach((n) => n.classList.remove('active'));
      item.classList.add('active');

      document.querySelectorAll('.view').forEach((v) => v.classList.remove('active'));
      const target = document.getElementById(`view-${item.dataset.view}`);
      if (target) target.classList.add('active');
    });
  });
}

// ---------------------------------------------------------------------
// Recipe generation
// ---------------------------------------------------------------------

function setupRecipeForm() {
  const form = document.getElementById('recipeForm');
  if (!form) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const btn = document.getElementById('generateBtn');
    const btnText = document.getElementById('generateBtnText');
    const spinner = document.getElementById('generateSpinner');

    btn.setAttribute('disabled', 'true');
    btnText.textContent = 'Cooking up your recipe...';
    spinner.classList.remove('hidden');

    try {
      const formData = new FormData(form);
      const response = await fetch('/api/generate-recipe', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errBody = await response.json().catch(() => ({}));
        throw new Error(errBody.detail || 'Failed to generate recipe.');
      }

      const recipe = await response.json();
      currentRecipe = recipe;
      currentRecipeId = null; // freshly generated, not yet saved
      renderRecipe(recipe);
      showToast('Recipe generated!', 'success');

      const resultArea = document.getElementById('resultArea');
      resultArea.classList.remove('hidden');
      resultArea.scrollIntoView({ behavior: 'smooth', block: 'start' });

    } catch (err) {
      showToast(err.message || 'Something went wrong.', 'error');
    } finally {
      btn.removeAttribute('disabled');
      btnText.textContent = 'Generate Recipe';
      spinner.classList.add('hidden');
    }
  });
}

function renderRecipe(recipe) {
  document.getElementById('recipeName').textContent = recipe.recipe_name || 'Untitled Recipe';
  document.getElementById('recipeDescription').textContent = recipe.description || '';
  document.getElementById('prepTime').textContent = recipe.prep_time || '—';
  document.getElementById('cookTime').textContent = recipe.cooking_time || '—';
  document.getElementById('ingredientsBlock').textContent = recipe.ingredients || '—';
  document.getElementById('instructionsBlock').textContent = recipe.instructions || '—';

  document.getElementById('nCalories').textContent = recipe.calories || '—';
  document.getElementById('nProtein').textContent = recipe.protein || '—';
  document.getElementById('nCarbs').textContent = recipe.carbs || '—';
  document.getElementById('nFat').textContent = recipe.fat || '—';

  document.getElementById('cookingTips').textContent = recipe.cooking_tips || '—';
  document.getElementById('storageTips').textContent = recipe.storage_tips || '—';
  document.getElementById('altIngredients').textContent = recipe.alternative_ingredients || '—';
  document.getElementById('servingSuggestions').textContent = recipe.serving_suggestions || '—';

  const ytBtn = document.getElementById('youtubeBtn');
  if (ytBtn && recipe.recipe_name) {
    ytBtn.href = 'https://www.youtube.com/results?search_query=' + encodeURIComponent(recipe.recipe_name + ' recipe');
  }

  // Download only becomes available once the recipe is saved (has an id + markdown on server)
  const downloadBtn = document.getElementById('downloadBtn');
  if (downloadBtn) downloadBtn.setAttribute('disabled', 'true');

  if (recipe.emoji) {
    updateStickers(recipe.emoji);
  }
}

function updateStickers(emoji) {
  document.querySelectorAll('.sticker').forEach(sticker => {
    sticker.textContent = emoji;
  });
}

// ---------------------------------------------------------------------
// Copy / Save / Download actions
// ---------------------------------------------------------------------

function setupRecipeActions() {
  const copyBtn = document.getElementById('copyBtn');
  const saveBtn = document.getElementById('saveBtn');
  const downloadBtn = document.getElementById('downloadBtn');

  if (copyBtn) {
    copyBtn.addEventListener('click', async () => {
      if (!currentRecipe) return;
      const text = currentRecipe.raw_markdown || buildPlainTextRecipe(currentRecipe);
      try {
        await navigator.clipboard.writeText(text);
        showToast('Recipe copied to clipboard!', 'success');
      } catch {
        showToast('Could not copy recipe.', 'error');
      }
    });
  }

  if (saveBtn) {
    saveBtn.addEventListener('click', async () => {
      if (!currentRecipe) return;
      saveBtn.setAttribute('disabled', 'true');
      try {
        const response = await fetch('/api/save-recipe', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(currentRecipe),
        });
        if (!response.ok) throw new Error('Failed to save recipe.');
        const result = await response.json();
        currentRecipeId = result.recipe.id;
        document.getElementById('downloadBtn').removeAttribute('disabled');
        showToast('Recipe saved to history!', 'success');
        prependHistoryCard(result.recipe);
      } catch (err) {
        showToast(err.message || 'Could not save recipe.', 'error');
      } finally {
        saveBtn.removeAttribute('disabled');
      }
    });
  }

  if (downloadBtn) {
    downloadBtn.addEventListener('click', () => {
      if (!currentRecipeId) {
        showToast('Save the recipe first to download it.', 'error');
        return;
      }
      window.location.href = `/api/recipe/${currentRecipeId}/download`;
    });
  }
}

function buildPlainTextRecipe(recipe) {
  return `${recipe.recipe_name}\n\n${recipe.description}\n\nIngredients:\n${recipe.ingredients}\n\nInstructions:\n${recipe.instructions}`;
}

// ---------------------------------------------------------------------
// History
// ---------------------------------------------------------------------

function setupHistoryOpeners() {
  document.querySelectorAll('.open-history-btn').forEach((btn) => {
    btn.addEventListener('click', async () => {
      const id = btn.dataset.recipeId;
      try {
        const response = await fetch(`/api/recipe/${id}`);
        if (!response.ok) throw new Error('Could not load recipe.');
        const recipe = await response.json();

        currentRecipe = recipe;
        currentRecipeId = recipe.id;
        renderRecipe(recipe);
        document.getElementById('downloadBtn').removeAttribute('disabled');

        // Switch to Generate view so the recipe card is visible
        document.querySelectorAll('.nav-item[data-view]').forEach((n) => n.classList.remove('active'));
        document.querySelector('.nav-item[data-view="generate"]').classList.add('active');
        document.querySelectorAll('.view').forEach((v) => v.classList.remove('active'));
        document.getElementById('view-generate').classList.add('active');

        document.getElementById('resultArea').classList.remove('hidden');
        window.scrollTo({ top: 0, behavior: 'smooth' });
      } catch (err) {
        showToast(err.message || 'Could not open recipe.', 'error');
      }
    });
  });
}

function prependHistoryCard(recipe) {
  const grid = document.getElementById('historyGrid');
  if (!grid) return;

  const emptyState = grid.querySelector('.empty-state');
  if (emptyState) emptyState.remove();

  const card = document.createElement('div');
  card.className = 'card history-item';
  card.dataset.recipeId = recipe.id;

  const shortDesc = (recipe.description || '').slice(0, 120);
  card.innerHTML = `
    <h3>${escapeHtml(recipe.recipe_name)}</h3>
    <p class="history-meta">${escapeHtml(recipe.cuisine || 'Any')} · ${escapeHtml(recipe.meal_type || 'Any')} · ${escapeHtml(recipe.cooking_time || '—')}</p>
    <p class="history-desc">${escapeHtml(shortDesc)}${(recipe.description || '').length > 120 ? '…' : ''}</p>
    <button class="btn-secondary open-history-btn" data-recipe-id="${recipe.id}">Open Recipe</button>
  `;
  grid.prepend(card);
  setupHistoryOpeners();
}

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

// ---------------------------------------------------------------------
// Toast notifications
// ---------------------------------------------------------------------

let toastTimeout = null;

function showToast(message, type = 'success') {
  const toast = document.getElementById('toast');
  toast.textContent = message;
  toast.className = `toast toast-${type}`;
  toast.classList.remove('hidden');

  clearTimeout(toastTimeout);
  toastTimeout = setTimeout(() => {
    toast.classList.add('hidden');
  }, 3200);
}
