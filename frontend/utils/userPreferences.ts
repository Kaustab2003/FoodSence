/**
 * User Preference Tracking System
 * 
 * PATENT INNOVATION: Session-based preference learning without persistent accounts
 * - Tracks user behavior via localStorage
 * - Adapts AI analysis based on detected patterns
 * - Privacy-preserving (ephemeral, no server storage)
 */

export interface UserPreferences {
  // Follow-up question interaction tracking
  followUpClicks: {
    childSafety: number;
    dailyConsumption: number;
    healthierAlternatives: number;
    weightLoss: number;
    allergyInfo: number;
    pregnancySafety: number;
  };
  
  // Insight reading time (in seconds)
  insightFocus: {
    [ingredientName: string]: number;
  };
  
  // Products analyzed
  analyzedProducts: Array<{
    productName: string;
    timestamp: number;
    category: string;
  }>;
  
  // Inferred user intent patterns
  detectedIntents: {
    healthFocused: number;
    childCare: number;
    weightManagement: number;
    allergyAware: number;
  };
}

const STORAGE_KEY = 'foodsense_user_preferences';

/**
 * Initialize or retrieve user preferences
 */
export function getUserPreferences(): UserPreferences {
  if (typeof window === 'undefined') {
    return getDefaultPreferences();
  }
  
  const stored = localStorage.getItem(STORAGE_KEY);
  
  if (stored) {
    try {
      return JSON.parse(stored);
    } catch (e) {
      console.warn('Failed to parse preferences, resetting');
      return getDefaultPreferences();
    }
  }
  
  return getDefaultPreferences();
}

/**
 * Save user preferences
 */
export function saveUserPreferences(prefs: UserPreferences): void {
  if (typeof window === 'undefined') return;
  
  localStorage.setItem(STORAGE_KEY, JSON.stringify(prefs));
}

/**
 * Track follow-up question click
 */
export function trackFollowUpClick(questionType: string): void {
  const prefs = getUserPreferences();
  
  // Map question text to category
  const category = categorizeQuestion(questionType);
  
  if (category && prefs.followUpClicks[category as keyof typeof prefs.followUpClicks] !== undefined) {
    prefs.followUpClicks[category as keyof typeof prefs.followUpClicks]++;
    
    // Update detected intents based on patterns
    updateDetectedIntents(prefs);
    
    saveUserPreferences(prefs);
  }
}

/**
 * Track time spent reading an insight
 */
export function trackInsightFocus(ingredientName: string, durationSeconds: number): void {
  const prefs = getUserPreferences();
  
  if (!prefs.insightFocus[ingredientName]) {
    prefs.insightFocus[ingredientName] = 0;
  }
  
  prefs.insightFocus[ingredientName] += durationSeconds;
  saveUserPreferences(prefs);
}

/**
 * Track analyzed product
 */
export function trackAnalyzedProduct(productName: string, category: string): void {
  const prefs = getUserPreferences();
  
  prefs.analyzedProducts.push({
    productName,
    timestamp: Date.now(),
    category
  });
  
  // Keep only last 20 products
  if (prefs.analyzedProducts.length > 20) {
    prefs.analyzedProducts = prefs.analyzedProducts.slice(-20);
  }
  
  saveUserPreferences(prefs);
}

/**
 * Get personalized intent hints for backend
 */
export function getPersonalizedIntents(): string[] {
  const prefs = getUserPreferences();
  const intents: string[] = [];
  
  // Child safety focus
  if (prefs.followUpClicks.childSafety >= 3 || prefs.detectedIntents.childCare > 50) {
    intents.push('child_safety_prioritize');
  }
  
  // Weight management focus
  if (prefs.followUpClicks.weightLoss >= 2 || prefs.detectedIntents.weightManagement > 40) {
    intents.push('weight_management_focus');
  }
  
  // General health optimization
  if (prefs.detectedIntents.healthFocused > 60) {
    intents.push('health_optimization');
  }
  
  // Allergy awareness
  if (prefs.followUpClicks.allergyInfo >= 2 || prefs.detectedIntents.allergyAware > 30) {
    intents.push('allergy_awareness');
  }
  
  return intents;
}

/**
 * Get preference summary for debugging
 */
export function getPreferenceSummary(): string {
  const prefs = getUserPreferences();
  const intents = getPersonalizedIntents();
  
  return `
📊 User Profile:
- Analyzed ${prefs.analyzedProducts.length} products
- Top concerns: ${intents.join(', ') || 'None yet'}
- Child safety clicks: ${prefs.followUpClicks.childSafety}
- Weight management clicks: ${prefs.followUpClicks.weightLoss}
  `.trim();
}

/**
 * Reset preferences (for testing)
 */
export function resetPreferences(): void {
  if (typeof window === 'undefined') return;
  localStorage.removeItem(STORAGE_KEY);
}

// ============= Helper Functions =============

function getDefaultPreferences(): UserPreferences {
  return {
    followUpClicks: {
      childSafety: 0,
      dailyConsumption: 0,
      healthierAlternatives: 0,
      weightLoss: 0,
      allergyInfo: 0,
      pregnancySafety: 0
    },
    insightFocus: {},
    analyzedProducts: [],
    detectedIntents: {
      healthFocused: 0,
      childCare: 0,
      weightManagement: 0,
      allergyAware: 0
    }
  };
}

function categorizeQuestion(questionText: string): string | null {
  const lower = questionText.toLowerCase();
  
  if (lower.includes('kid') || lower.includes('child')) return 'childSafety';
  if (lower.includes('daily') || lower.includes('often')) return 'dailyConsumption';
  if (lower.includes('alternative') || lower.includes('better')) return 'healthierAlternatives';
  if (lower.includes('weight') || lower.includes('lose') || lower.includes('diet')) return 'weightLoss';
  if (lower.includes('allerg')) return 'allergyInfo';
  if (lower.includes('pregnan')) return 'pregnancySafety';
  
  return null;
}

function updateDetectedIntents(prefs: UserPreferences): void {
  // Child care intent
  prefs.detectedIntents.childCare = Math.min(100, 
    prefs.followUpClicks.childSafety * 20 + 
    prefs.followUpClicks.pregnancySafety * 15
  );
  
  // Weight management intent
  prefs.detectedIntents.weightManagement = Math.min(100,
    prefs.followUpClicks.weightLoss * 25 +
    prefs.followUpClicks.dailyConsumption * 10
  );
  
  // Health focused intent
  prefs.detectedIntents.healthFocused = Math.min(100,
    prefs.followUpClicks.healthierAlternatives * 20 +
    Object.keys(prefs.insightFocus).length * 5
  );
  
  // Allergy aware intent
  prefs.detectedIntents.allergyAware = Math.min(100,
    prefs.followUpClicks.allergyInfo * 30
  );
}
