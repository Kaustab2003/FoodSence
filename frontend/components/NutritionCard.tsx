import React from 'react';

interface NutritionAnalysis {
  classification: 'Good' | 'Moderate' | 'Bad';
  confidence: 'High' | 'Medium' | 'Low';
  key_positives: string[];
  key_negatives: string[];
  health_summary: string;
  recommended_consumption: 'Regular' | 'Occasional' | 'Avoid';
  nutrition_score: number;
  metrics: {
    positive_score: number;
    negative_score: number;
    critical_flags: number;
  };
}

interface NutritionData {
  serving_size?: string;
  servings_per_pack?: number;
  calories?: number;
  protein?: number;
  carbohydrates?: number;
  total_sugars?: number;
  added_sugars?: number;
  total_fat?: number;
  saturated_fat?: number;
  mufa_fat?: number;
  pufa_fat?: number;
  trans_fat?: number;
  cholesterol?: number;
  sodium?: number;
  dietary_fiber?: number | string;
  per_100g?: boolean;
}

interface NutritionCardProps {
  analysis: NutritionAnalysis;
  nutritionData: NutritionData;
}

export default function NutritionCard({ analysis, nutritionData }: NutritionCardProps) {
  // Get color scheme based on classification
  const getColorScheme = () => {
    switch (analysis.classification) {
      case 'Good':
        return {
          bg: 'bg-green-50',
          border: 'border-green-200',
          badge: 'bg-green-500',
          text: 'text-green-800',
          icon: '✅'
        };
      case 'Moderate':
        return {
          bg: 'bg-yellow-50',
          border: 'border-yellow-200',
          badge: 'bg-yellow-500',
          text: 'text-yellow-800',
          icon: '⚠️'
        };
      case 'Bad':
        return {
          bg: 'bg-red-50',
          border: 'border-red-200',
          badge: 'bg-red-500',
          text: 'text-red-800',
          icon: '❌'
        };
      default:
        return {
          bg: 'bg-gray-50',
          border: 'border-gray-200',
          badge: 'bg-gray-500',
          text: 'text-gray-800',
          icon: '❓'
        };
    }
  };

  const colors = getColorScheme();

  // Get recommendation badge color
  const getRecommendationColor = () => {
    switch (analysis.recommended_consumption) {
      case 'Regular':
        return 'bg-green-100 text-green-800 border-green-300';
      case 'Occasional':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'Avoid':
        return 'bg-red-100 text-red-800 border-red-300';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  // Format number for display
  const formatValue = (value: any): string => {
    if (value === null || value === undefined || value === 'Not listed') return 'N/A';
    if (typeof value === 'number') return value.toFixed(1);
    return String(value);
  };

  return (
    <div className={`${colors.bg} ${colors.border} border-2 rounded-xl p-6 shadow-lg mb-6`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className={`${colors.badge} text-white w-12 h-12 rounded-full flex items-center justify-center text-2xl font-bold shadow-md`}>
            {colors.icon}
          </div>
          <div>
            <h2 className={`text-2xl font-bold ${colors.text}`}>
              Nutrition Analysis
            </h2>
            <div className="flex items-center space-x-2 mt-1">
              <span className={`text-sm font-medium ${colors.text}`}>
                Classification: {analysis.classification}
              </span>
              <span className="text-gray-400">•</span>
              <span className="text-sm text-gray-600">
                Confidence: {analysis.confidence}
              </span>
            </div>
          </div>
        </div>
        
        {/* Score Badge */}
        <div className="text-center">
          <div className={`${colors.badge} text-white rounded-full w-20 h-20 flex flex-col items-center justify-center shadow-lg`}>
            <span className="text-2xl font-bold">{analysis.nutrition_score}</span>
            <span className="text-xs">Score</span>
          </div>
        </div>
      </div>

      {/* Health Summary */}
      <div className="bg-white rounded-lg p-4 mb-4 border border-gray-200">
        <p className="text-gray-800 leading-relaxed">
          {analysis.health_summary}
        </p>
      </div>

      {/* Recommendation */}
      <div className={`${getRecommendationColor()} rounded-lg px-4 py-3 mb-4 border-2 flex items-center space-x-2`}>
        <span className="font-bold text-sm">Recommended Consumption:</span>
        <span className="font-bold text-lg">{analysis.recommended_consumption}</span>
      </div>

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        {/* Positives */}
        {analysis.key_positives.length > 0 && (
          <div className="bg-white rounded-lg p-4 border border-green-200">
            <h3 className="font-semibold text-green-700 mb-2 flex items-center">
              <span className="mr-2">✅</span>
              Positive Aspects
            </h3>
            <ul className="space-y-1">
              {analysis.key_positives.map((positive, idx) => (
                <li key={idx} className="text-sm text-gray-700 flex items-start">
                  <span className="text-green-500 mr-2 mt-1">•</span>
                  <span>{positive}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Negatives */}
        {analysis.key_negatives.length > 0 && (
          <div className="bg-white rounded-lg p-4 border border-red-200">
            <h3 className="font-semibold text-red-700 mb-2 flex items-center">
              <span className="mr-2">⚠️</span>
              Concerns
            </h3>
            <ul className="space-y-1">
              {analysis.key_negatives.map((negative, idx) => (
                <li key={idx} className="text-sm text-gray-700 flex items-start">
                  <span className="text-red-500 mr-2 mt-1">•</span>
                  <span>{negative.replace('⚠️ CRITICAL: ', '')}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Nutrition Facts Table */}
      <div className="bg-white rounded-lg p-4 border border-gray-200">
        <h3 className="font-bold text-gray-800 mb-3 flex items-center">
          <span className="mr-2">📊</span>
          Nutrition Facts
          {nutritionData.serving_size && (
            <span className="ml-2 text-sm font-normal text-gray-600">
              (Per Serving: {nutritionData.serving_size})
            </span>
          )}
        </h3>
        
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {/* Calories */}
          <div className="bg-gray-50 rounded p-2">
            <div className="text-xs text-gray-600">Calories</div>
            <div className="text-lg font-bold text-gray-800">{formatValue(nutritionData.calories)} kcal</div>
          </div>

          {/* Protein */}
          <div className="bg-gray-50 rounded p-2">
            <div className="text-xs text-gray-600">Protein</div>
            <div className="text-lg font-bold text-green-700">{formatValue(nutritionData.protein)} g</div>
          </div>

          {/* Carbs */}
          <div className="bg-gray-50 rounded p-2">
            <div className="text-xs text-gray-600">Carbohydrates</div>
            <div className="text-lg font-bold text-gray-800">{formatValue(nutritionData.carbohydrates)} g</div>
          </div>

          {/* Total Sugars */}
          {nutritionData.total_sugars !== undefined && (
            <div className="bg-gray-50 rounded p-2">
              <div className="text-xs text-gray-600">Total Sugars</div>
              <div className="text-lg font-bold text-orange-600">{formatValue(nutritionData.total_sugars)} g</div>
            </div>
          )}

          {/* Added Sugars */}
          {nutritionData.added_sugars !== undefined && (
            <div className="bg-gray-50 rounded p-2">
              <div className="text-xs text-gray-600">Added Sugars</div>
              <div className="text-lg font-bold text-red-600">{formatValue(nutritionData.added_sugars)} g</div>
            </div>
          )}

          {/* Total Fat */}
          <div className="bg-gray-50 rounded p-2">
            <div className="text-xs text-gray-600">Total Fat</div>
            <div className="text-lg font-bold text-gray-800">{formatValue(nutritionData.total_fat)} g</div>
          </div>

          {/* Saturated Fat */}
          {nutritionData.saturated_fat !== undefined && (
            <div className="bg-gray-50 rounded p-2">
              <div className="text-xs text-gray-600">Saturated Fat</div>
              <div className="text-lg font-bold text-red-600">{formatValue(nutritionData.saturated_fat)} g</div>
            </div>
          )}

          {/* Trans Fat */}
          {nutritionData.trans_fat !== undefined && (
            <div className="bg-gray-50 rounded p-2">
              <div className="text-xs text-gray-600">Trans Fat</div>
              <div className={`text-lg font-bold ${nutritionData.trans_fat === 0 ? 'text-green-600' : 'text-red-700'}`}>
                {formatValue(nutritionData.trans_fat)} g
              </div>
            </div>
          )}

          {/* Sodium */}
          {nutritionData.sodium !== undefined && (
            <div className="bg-gray-50 rounded p-2">
              <div className="text-xs text-gray-600">Sodium</div>
              <div className="text-lg font-bold text-gray-800">{formatValue(nutritionData.sodium)} mg</div>
            </div>
          )}

          {/* Cholesterol */}
          {nutritionData.cholesterol !== undefined && (
            <div className="bg-gray-50 rounded p-2">
              <div className="text-xs text-gray-600">Cholesterol</div>
              <div className="text-lg font-bold text-gray-800">{formatValue(nutritionData.cholesterol)} mg</div>
            </div>
          )}

          {/* Dietary Fiber */}
          {nutritionData.dietary_fiber && nutritionData.dietary_fiber !== 'Not listed' && (
            <div className="bg-gray-50 rounded p-2">
              <div className="text-xs text-gray-600">Dietary Fiber</div>
              <div className="text-lg font-bold text-green-700">{formatValue(nutritionData.dietary_fiber)} g</div>
            </div>
          )}

          {/* MUFA */}
          {nutritionData.mufa_fat !== undefined && nutritionData.mufa_fat !== null && (
            <div className="bg-gray-50 rounded p-2">
              <div className="text-xs text-gray-600">MUFA Fat</div>
              <div className="text-lg font-bold text-green-600">{formatValue(nutritionData.mufa_fat)} g</div>
            </div>
          )}

          {/* PUFA */}
          {nutritionData.pufa_fat !== undefined && nutritionData.pufa_fat !== null && (
            <div className="bg-gray-50 rounded p-2">
              <div className="text-xs text-gray-600">PUFA Fat</div>
              <div className="text-lg font-bold text-green-600">{formatValue(nutritionData.pufa_fat)} g</div>
            </div>
          )}
        </div>

        {/* Servings Info */}
        {nutritionData.servings_per_pack && (
          <div className="mt-3 pt-3 border-t border-gray-200">
            <p className="text-sm text-gray-600">
              <span className="font-semibold">Package contains:</span> {nutritionData.servings_per_pack} servings
            </p>
          </div>
        )}
      </div>

      {/* Critical Flags Warning */}
      {analysis.metrics.critical_flags > 0 && (
        <div className="mt-4 bg-red-50 border-2 border-red-300 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <span className="text-2xl">⚠️</span>
            <div>
              <h4 className="font-bold text-red-800">Critical Health Flags Detected</h4>
              <p className="text-sm text-red-700">
                This product has {analysis.metrics.critical_flags} critical health concern(s) that require attention.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
