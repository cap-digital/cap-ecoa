import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { dashboardApi } from "../services/api";
import { Card, CardHeader, CardTitle, CardContent } from "../components/ui/Card";
import { Badge, SentimentBadge } from "../components/ui/Badge";
import { formatRelativeTime } from "../lib/utils";
import {
  Newspaper,
  TrendingUp,
  TrendingDown,
  Minus,
  Filter,
  ExternalLink,
  Loader2,
} from "lucide-react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";

interface Stats {
  total_news: number;
  news_today: number;
  positive_mentions: number;
  negative_mentions: number;
  neutral_mentions: number;
  active_terms: number;
}

interface TrendData {
  term: string;
  data: Array<{ date: string; count: number; sentiment_avg: number }>;
}

interface SourceStats {
  source: string;
  count: number;
  percentage: number;
  [key: string]: string | number;
}

interface RecentNews {
  id: string;
  title: string;
  source: string;
  sentiment: string;
  published_at: string;
  image_url: string | null;
}

const COLORS = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444"];

export function Dashboard() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [trends, setTrends] = useState<TrendData[]>([]);
  const [sources, setSources] = useState<SourceStats[]>([]);
  const [recentNews, setRecentNews] = useState<RecentNews[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadDashboard() {
      try {
        const response = await dashboardApi.getAll();
        const { stats, trends, sources, recent_news } = response.data;
        setStats(stats);
        setTrends(trends);
        setSources(sources);
        setRecentNews(recent_news);
      } catch (error) {
        console.error("Error loading dashboard:", error);
      } finally {
        setLoading(false);
      }
    }
    loadDashboard();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-500">Visão geral das suas menções na mídia</p>
        </div>
        <Link
          to="/filters"
          className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        >
          <Filter className="w-4 h-4" />
          <span>Gerenciar Filtros</span>
        </Link>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="flex items-center space-x-4">
            <div className="p-3 bg-blue-100 rounded-lg">
              <Newspaper className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Total de Notícias</p>
              <p className="text-2xl font-bold text-gray-900">{stats?.total_news || 0}</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="flex items-center space-x-4">
            <div className="p-3 bg-green-100 rounded-lg">
              <TrendingUp className="w-6 h-6 text-green-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Menções Positivas</p>
              <p className="text-2xl font-bold text-green-600">{stats?.positive_mentions || 0}</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="flex items-center space-x-4">
            <div className="p-3 bg-red-100 rounded-lg">
              <TrendingDown className="w-6 h-6 text-red-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Menções Negativas</p>
              <p className="text-2xl font-bold text-red-600">{stats?.negative_mentions || 0}</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="flex items-center space-x-4">
            <div className="p-3 bg-gray-100 rounded-lg">
              <Minus className="w-6 h-6 text-gray-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Menções Neutras</p>
              <p className="text-2xl font-bold text-gray-600">{stats?.neutral_mentions || 0}</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Trend Chart */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Tendência de Menções (7 dias)</CardTitle>
          </CardHeader>
          <CardContent>
            {trends.length > 0 && trends[0].data.length > 0 ? (
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={trends[0].data}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                    <YAxis tick={{ fontSize: 12 }} />
                    <Tooltip />
                    <Line
                      type="monotone"
                      dataKey="count"
                      stroke="#3b82f6"
                      strokeWidth={2}
                      dot={{ fill: "#3b82f6" }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div className="h-64 flex items-center justify-center text-gray-500">
                <p>Adicione filtros para ver tendências</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Sources Pie Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Distribuição por Fonte</CardTitle>
          </CardHeader>
          <CardContent>
            {sources.length > 0 ? (
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={sources}
                      cx="50%"
                      cy="50%"
                      innerRadius={40}
                      outerRadius={80}
                      paddingAngle={5}
                      dataKey="count"
                      nameKey="source"
                      label={({ name }) => String(name).toUpperCase()}
                    >
                      {sources.map((_, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div className="h-64 flex items-center justify-center text-gray-500">
                <p>Sem dados disponíveis</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Recent News */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Notícias Recentes</CardTitle>
          <Link
            to="/news"
            className="text-sm text-primary-600 hover:text-primary-700 font-medium"
          >
            Ver todas
          </Link>
        </CardHeader>
        <CardContent>
          {recentNews.length > 0 ? (
            <div className="space-y-4">
              {recentNews.map((news) => (
                <div
                  key={news.id}
                  className="flex items-start space-x-4 p-4 rounded-lg border border-gray-100 hover:bg-gray-50 transition-colors"
                >
                  {news.image_url && (
                    <img
                      src={news.image_url}
                      alt=""
                      className="w-20 h-20 object-cover rounded-lg flex-shrink-0"
                    />
                  )}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between">
                      <h4 className="text-sm font-medium text-gray-900 line-clamp-2">
                        {news.title}
                      </h4>
                      <Link
                        to={`/news/${news.id}`}
                        className="ml-2 text-gray-400 hover:text-primary-600"
                      >
                        <ExternalLink className="w-4 h-4" />
                      </Link>
                    </div>
                    <div className="flex items-center space-x-2 mt-2">
                      <Badge>{news.source.toUpperCase()}</Badge>
                      <SentimentBadge sentiment={news.sentiment} />
                      <span className="text-xs text-gray-500">
                        {formatRelativeTime(news.published_at)}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <Newspaper className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p>Nenhuma notícia encontrada</p>
              <p className="text-sm mt-1">
                Adicione filtros para começar a monitorar
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
