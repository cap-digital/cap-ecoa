import { useEffect, useState } from "react";
import { newsApi } from "../services/api";
import { Card, CardContent } from "../components/ui/Card";
import { Button } from "../components/ui/Button";
import { Badge, SentimentBadge } from "../components/ui/Badge";
import { formatDate, formatRelativeTime } from "../lib/utils";
import {
  Search,
  Filter,
  ExternalLink,
  Loader2,
  ChevronLeft,
  ChevronRight,
  Newspaper,
  X,
} from "lucide-react";

interface News {
  id: string;
  title: string;
  summary: string | null;
  url: string;
  image_url: string | null;
  author: string | null;
  source: string;
  sentiment: string | null;
  published_at: string | null;
  matched_terms: string[];
}

interface NewsResponse {
  items: News[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

export function NewsPage() {
  const [news, setNews] = useState<News[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedSource, setSelectedSource] = useState<string>("");
  const [selectedSentiment, setSelectedSentiment] = useState<string>("");
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);
  const [showFilters, setShowFilters] = useState(false);

  const sources = [
    { value: "", label: "Todas as fontes" },
    { value: "g1", label: "G1" },
    { value: "cnn", label: "CNN Brasil" },
    { value: "twitter", label: "Twitter" },
    { value: "threads", label: "Threads" },
  ];

  const sentiments = [
    { value: "", label: "Todos os sentimentos" },
    { value: "positive", label: "Positivo" },
    { value: "negative", label: "Negativo" },
    { value: "neutral", label: "Neutro" },
  ];

  useEffect(() => {
    loadNews();
  }, [page, selectedSource, selectedSentiment]);

  async function loadNews() {
    setLoading(true);
    try {
      const response = await newsApi.list({
        term: searchTerm || undefined,
        source: selectedSource || undefined,
        sentiment: selectedSentiment || undefined,
        page,
        per_page: 20,
      });
      const data: NewsResponse = response.data;
      setNews(data.items);
      setTotalPages(data.total_pages);
      setTotal(data.total);
    } catch (error) {
      console.error("Error loading news:", error);
    } finally {
      setLoading(false);
    }
  }

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    loadNews();
  };

  const clearFilters = () => {
    setSearchTerm("");
    setSelectedSource("");
    setSelectedSentiment("");
    setPage(1);
  };

  const hasActiveFilters = searchTerm || selectedSource || selectedSentiment;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Notícias</h1>
          <p className="text-gray-500">
            {total} notícias encontradas
          </p>
        </div>
        <Button
          variant="secondary"
          onClick={() => setShowFilters(!showFilters)}
          className="md:hidden"
        >
          <Filter className="w-4 h-4 mr-2" />
          Filtros
        </Button>
      </div>

      {/* Search and Filters */}
      <Card>
        <CardContent className="p-4">
          <form onSubmit={handleSearch} className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Buscar por termo..."
                className="w-full pl-10 pr-4 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500"
              />
            </div>

            <div className={`flex flex-col md:flex-row gap-4 ${showFilters ? "" : "hidden md:flex"}`}>
              <select
                value={selectedSource}
                onChange={(e) => {
                  setSelectedSource(e.target.value);
                  setPage(1);
                }}
                className="px-4 py-2 rounded-lg border border-gray-300 bg-white focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500"
              >
                {sources.map((source) => (
                  <option key={source.value} value={source.value}>
                    {source.label}
                  </option>
                ))}
              </select>

              <select
                value={selectedSentiment}
                onChange={(e) => {
                  setSelectedSentiment(e.target.value);
                  setPage(1);
                }}
                className="px-4 py-2 rounded-lg border border-gray-300 bg-white focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500"
              >
                {sentiments.map((sentiment) => (
                  <option key={sentiment.value} value={sentiment.value}>
                    {sentiment.label}
                  </option>
                ))}
              </select>

              <Button type="submit">Buscar</Button>

              {hasActiveFilters && (
                <Button type="button" variant="ghost" onClick={clearFilters}>
                  <X className="w-4 h-4 mr-1" />
                  Limpar
                </Button>
              )}
            </div>
          </form>
        </CardContent>
      </Card>

      {/* News List */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
        </div>
      ) : news.length > 0 ? (
        <div className="space-y-4">
          {news.map((item) => (
            <Card key={item.id} className="hover:shadow-md transition-shadow">
              <CardContent className="p-0">
                <div className="flex flex-col md:flex-row">
                  {item.image_url && (
                    <div className="md:w-48 h-48 md:h-auto flex-shrink-0">
                      <img
                        src={item.image_url}
                        alt=""
                        className="w-full h-full object-cover rounded-t-xl md:rounded-l-xl md:rounded-tr-none"
                      />
                    </div>
                  )}
                  <div className="flex-1 p-6">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-gray-900 line-clamp-2 mb-2">
                          {item.title}
                        </h3>
                        {item.summary && (
                          <p className="text-gray-600 text-sm line-clamp-2 mb-3">
                            {item.summary}
                          </p>
                        )}
                      </div>
                      <a
                        href={item.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="ml-4 p-2 text-gray-400 hover:text-primary-600 hover:bg-gray-100 rounded-lg transition-colors"
                      >
                        <ExternalLink className="w-5 h-5" />
                      </a>
                    </div>

                    <div className="flex flex-wrap items-center gap-2 mt-4">
                      <Badge>{item.source.toUpperCase()}</Badge>
                      <SentimentBadge sentiment={item.sentiment} />
                      {item.matched_terms.slice(0, 3).map((term) => (
                        <Badge key={term} variant="neutral">
                          {term}
                        </Badge>
                      ))}
                      {item.matched_terms.length > 3 && (
                        <Badge variant="default">
                          +{item.matched_terms.length - 3}
                        </Badge>
                      )}
                    </div>

                    <div className="flex items-center justify-between mt-4 pt-4 border-t border-gray-100">
                      <div className="text-sm text-gray-500">
                        {item.author && <span>{item.author} · </span>}
                        {item.published_at && (
                          <span title={formatDate(item.published_at)}>
                            {formatRelativeTime(item.published_at)}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-center space-x-4 mt-8">
              <Button
                variant="secondary"
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
              >
                <ChevronLeft className="w-4 h-4 mr-1" />
                Anterior
              </Button>
              <span className="text-sm text-gray-600">
                Página {page} de {totalPages}
              </span>
              <Button
                variant="secondary"
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
              >
                Próxima
                <ChevronRight className="w-4 h-4 ml-1" />
              </Button>
            </div>
          )}
        </div>
      ) : (
        <Card>
          <CardContent className="text-center py-12">
            <Newspaper className="w-16 h-16 mx-auto mb-4 text-gray-300" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Nenhuma notícia encontrada
            </h3>
            <p className="text-gray-500 mb-4">
              Adicione termos de monitoramento para começar a receber notícias
            </p>
            <Button variant="primary" onClick={() => window.location.href = "/filters"}>
              <Filter className="w-4 h-4 mr-2" />
              Gerenciar Filtros
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
