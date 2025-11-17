'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import { TrendingUp, TrendingDown, Activity, AlertCircle, CheckCircle, Clock, DollarSign } from 'lucide-react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface Signal {
  coin: string;
  timestamp: string;
  action: string;
  confidence: number;
  current_price: number;
  entry_price?: number;
  target_price?: number;
  stop_loss?: number;
  potential_profit_percent?: number;
  risk_level: string;
  scores: {
    technical: number;
    ai_prediction: number;
    sentiment: number;
  };
  analysis: any;
  reasoning: string[];
}

export default function Dashboard() {
  const [currentSignal, setCurrentSignal] = useState<Signal | null>(null);
  const [signalHistory, setSignalHistory] = useState<Signal[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedCoin, setSelectedCoin] = useState('BTC');
  const [coins] = useState(['BTC', 'ETH', 'BNB', 'SOL', 'ADA']);

  useEffect(() => {
    fetchSignalHistory();
  }, []);

  const fetchSignalHistory = async () => {
    try {
      const response = await axios.get(`${API_URL}/signals/latest?limit=10`);
      setSignalHistory(response.data.signals || []);
      if (response.data.signals && response.data.signals.length > 0) {
        setCurrentSignal(response.data.signals[0]);
      }
    } catch (error) {
      console.error('Error fetching signal history:', error);
    }
  };

  const scanCoin = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_URL}/signals/scan/${selectedCoin}`);
      setCurrentSignal(response.data);
      await fetchSignalHistory();
    } catch (error) {
      console.error('Error scanning coin:', error);
      alert('فشل في تحليل العملة. تأكد من تشغيل Backend API.');
    } finally {
      setLoading(false);
    }
  };

  const scanAllCoins = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_URL}/signals/scan-all`);
      if (response.data.signals && response.data.signals.length > 0) {
        setCurrentSignal(response.data.signals[0]);
      }
      await fetchSignalHistory();
    } catch (error) {
      console.error('Error scanning all coins:', error);
      alert('فشل في فحص جميع العملات. تأكد من تشغيل Backend API.');
    } finally {
      setLoading(false);
    }
  };

  const getActionColor = (action: string) => {
    if (action === 'BUY') return 'text-green-600 bg-green-100';
    if (action === 'SELL') return 'text-red-600 bg-red-100';
    return 'text-gray-600 bg-gray-100';
  };

  const getRiskColor = (risk: string) => {
    if (risk === 'LOW') return 'text-green-600';
    if (risk === 'MEDIUM') return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white p-6" dir="rtl">
      {/* Header */}
      <div className="max-w-7xl mx-auto mb-8">
        <h1 className="text-4xl font-bold mb-2 bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-400">
          🤖 نظام إشارات التداول بالذكاء الاصطناعي
        </h1>
        <p className="text-gray-400">تحليل متقدم باستخدام التعلم الآلي والتحليل الفني والمعنوي</p>
      </div>

      {/* Controls */}
      <div className="max-w-7xl mx-auto mb-8 bg-slate-800 rounded-lg p-6 shadow-xl">
        <div className="flex gap-4 flex-wrap items-center">
          <select
            value={selectedCoin}
            onChange={(e) => setSelectedCoin(e.target.value)}
            className="px-4 py-2 bg-slate-700 rounded-lg text-white focus:ring-2 focus:ring-purple-500 outline-none"
          >
            {coins.map((coin) => (
              <option key={coin} value={coin}>{coin}/USDT</option>
            ))}
          </select>

          <button
            onClick={scanCoin}
            disabled={loading}
            className="px-6 py-2 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg font-semibold hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          >
            {loading ? 'جاري التحليل...' : `تحليل ${selectedCoin}`}
          </button>

          <button
            onClick={scanAllCoins}
            disabled={loading}
            className="px-6 py-2 bg-gradient-to-r from-green-600 to-teal-600 rounded-lg font-semibold hover:from-green-700 hover:to-teal-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          >
            {loading ? 'جاري الفحص...' : 'فحص جميع العملات'}
          </button>

          <button
            onClick={fetchSignalHistory}
            className="px-6 py-2 bg-slate-700 rounded-lg font-semibold hover:bg-slate-600 transition-all"
          >
            تحديث
          </button>
        </div>
      </div>

      {/* Current Signal */}
      {currentSignal && (
        <div className="max-w-7xl mx-auto mb-8">
          <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-lg p-8 shadow-2xl border border-slate-700">
            {/* Signal Header */}
            <div className="flex justify-between items-start mb-6">
              <div>
                <div className="flex items-center gap-3 mb-2">
                  <h2 className="text-3xl font-bold">{currentSignal.coin}/USDT</h2>
                  <span className={`px-4 py-1 rounded-full font-bold text-lg ${getActionColor(currentSignal.action)}`}>
                    {currentSignal.action === 'BUY' && '📈 شراء'}
                    {currentSignal.action === 'SELL' && '📉 بيع'}
                    {currentSignal.action === 'HOLD' && '⏸️ انتظار'}
                  </span>
                </div>
                <p className="text-gray-400 flex items-center gap-2">
                  <Clock className="w-4 h-4" />
                  {new Date(currentSignal.timestamp).toLocaleString('ar-SA')}
                </p>
              </div>
              <div className="text-left">
                <div className="text-sm text-gray-400 mb-1">مستوى الثقة</div>
                <div className="text-4xl font-bold text-green-400">{currentSignal.confidence}%</div>
              </div>
            </div>

            {/* Price Information */}
            {currentSignal.action !== 'HOLD' && (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <div className="bg-slate-700 rounded-lg p-4">
                  <div className="text-sm text-gray-400 mb-1">السعر الحالي</div>
                  <div className="text-2xl font-bold">${currentSignal.current_price.toLocaleString()}</div>
                </div>
                <div className="bg-green-900/30 rounded-lg p-4 border border-green-700">
                  <div className="text-sm text-gray-400 mb-1">السعر المستهدف</div>
                  <div className="text-2xl font-bold text-green-400">${currentSignal.target_price?.toLocaleString()}</div>
                </div>
                <div className="bg-red-900/30 rounded-lg p-4 border border-red-700">
                  <div className="text-sm text-gray-400 mb-1">وقف الخسارة</div>
                  <div className="text-2xl font-bold text-red-400">${currentSignal.stop_loss?.toLocaleString()}</div>
                </div>
                <div className="bg-blue-900/30 rounded-lg p-4 border border-blue-700">
                  <div className="text-sm text-gray-400 mb-1">الربح المتوقع</div>
                  <div className="text-2xl font-bold text-blue-400">+{currentSignal.potential_profit_percent}%</div>
                </div>
              </div>
            )}

            {/* Risk Level */}
            <div className="mb-6">
              <div className="flex items-center gap-2 mb-2">
                <AlertCircle className="w-5 h-5" />
                <span className="font-semibold">مستوى المخاطرة:</span>
                <span className={`font-bold ${getRiskColor(currentSignal.risk_level)}`}>
                  {currentSignal.risk_level === 'LOW' && 'منخفض'}
                  {currentSignal.risk_level === 'MEDIUM' && 'متوسط'}
                  {currentSignal.risk_level === 'HIGH' && 'مرتفع'}
                </span>
              </div>
            </div>

            {/* Analysis Scores */}
            <div className="mb-6">
              <h3 className="font-semibold mb-3 flex items-center gap-2">
                <Activity className="w-5 h-5" />
                نتائج التحليل
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-slate-700 rounded-lg p-4">
                  <div className="text-sm text-gray-400 mb-2">التحليل الفني</div>
                  <div className="flex items-center justify-between">
                    <div className="text-2xl font-bold">{currentSignal.scores.technical}%</div>
                    <div className="w-24 h-2 bg-slate-600 rounded-full overflow-hidden">
                      <div className="h-full bg-blue-500" style={{ width: `${currentSignal.scores.technical}%` }}></div>
                    </div>
                  </div>
                </div>
                <div className="bg-slate-700 rounded-lg p-4">
                  <div className="text-sm text-gray-400 mb-2">توقع الذكاء الاصطناعي</div>
                  <div className="flex items-center justify-between">
                    <div className="text-2xl font-bold">{currentSignal.scores.ai_prediction}%</div>
                    <div className="w-24 h-2 bg-slate-600 rounded-full overflow-hidden">
                      <div className="h-full bg-purple-500" style={{ width: `${currentSignal.scores.ai_prediction}%` }}></div>
                    </div>
                  </div>
                </div>
                <div className="bg-slate-700 rounded-lg p-4">
                  <div className="text-sm text-gray-400 mb-2">التحليل المعنوي</div>
                  <div className="flex items-center justify-between">
                    <div className="text-2xl font-bold">{currentSignal.scores.sentiment}%</div>
                    <div className="w-24 h-2 bg-slate-600 rounded-full overflow-hidden">
                      <div className="h-full bg-green-500" style={{ width: `${currentSignal.scores.sentiment}%` }}></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Reasoning */}
            <div>
              <h3 className="font-semibold mb-3 flex items-center gap-2">
                <CheckCircle className="w-5 h-5" />
                أسباب الإشارة
              </h3>
              <div className="bg-slate-700/50 rounded-lg p-4 space-y-2">
                {currentSignal.reasoning.map((reason, idx) => (
                  <div key={idx} className="flex items-start gap-2">
                    <span className="text-green-400 mt-1">✓</span>
                    <span className="text-gray-300">{reason}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Signal History */}
      {signalHistory.length > 0 && (
        <div className="max-w-7xl mx-auto">
          <h2 className="text-2xl font-bold mb-4">سجل الإشارات السابقة</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {signalHistory.map((signal, idx) => (
              <div
                key={idx}
                onClick={() => setCurrentSignal(signal)}
                className="bg-slate-800 rounded-lg p-4 cursor-pointer hover:bg-slate-700 transition-all border border-slate-700 hover:border-purple-500"
              >
                <div className="flex justify-between items-start mb-2">
                  <span className="font-bold text-lg">{signal.coin}</span>
                  <span className={`px-3 py-1 rounded-full text-sm font-bold ${getActionColor(signal.action)}`}>
                    {signal.action}
                  </span>
                </div>
                <div className="text-sm text-gray-400 mb-2">
                  {new Date(signal.timestamp).toLocaleString('ar-SA')}
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-400">الثقة:</span>
                  <span className="font-bold text-green-400">{signal.confidence}%</span>
                </div>
                {signal.potential_profit_percent && (
                  <div className="flex justify-between items-center mt-1">
                    <span className="text-gray-400">الربح المتوقع:</span>
                    <span className="font-bold text-blue-400">+{signal.potential_profit_percent}%</span>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Empty State */}
      {!currentSignal && !loading && (
        <div className="max-w-7xl mx-auto text-center py-20">
          <Activity className="w-16 h-16 mx-auto mb-4 text-gray-600" />
          <h3 className="text-2xl font-bold mb-2 text-gray-400">لا توجد إشارات بعد</h3>
          <p className="text-gray-500 mb-6">اختر عملة وابدأ التحليل للحصول على إشارات تداول عالية الجودة</p>
          <button
            onClick={() => scanCoin()}
            className="px-8 py-3 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg font-semibold hover:from-blue-700 hover:to-purple-700 transition-all"
          >
            ابدأ التحليل الآن
          </button>
        </div>
      )}
    </div>
  );
}
