import { useEffect, useState } from "react";
import { filtersApi } from "../services/api";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../components/ui/Card";
import { Button } from "../components/ui/Button";
import { Input } from "../components/ui/Input";
import { Badge } from "../components/ui/Badge";
import {
  Plus,
  Trash2,
  Power,
  PowerOff,
  AlertCircle,
  Loader2,
  Filter,
  Crown,
} from "lucide-react";

interface FilterItem {
  id: string;
  term: string;
  is_active: boolean;
  created_at: string;
  match_count: number;
}

interface FiltersResponse {
  items: FilterItem[];
  total: number;
  limit_reached: boolean;
  plan_limit: number;
}

export function FiltersPage() {
  const [filters, setFilters] = useState<FilterItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [newTerm, setNewTerm] = useState("");
  const [adding, setAdding] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [limitReached, setLimitReached] = useState(false);
  const [planLimit, setPlanLimit] = useState(3);

  useEffect(() => {
    loadFilters();
  }, []);

  async function loadFilters() {
    try {
      const response = await filtersApi.list();
      const data: FiltersResponse = response.data;
      setFilters(data.items);
      setLimitReached(data.limit_reached);
      setPlanLimit(data.plan_limit);
    } catch (error) {
      console.error("Error loading filters:", error);
    } finally {
      setLoading(false);
    }
  }

  async function handleAddFilter(e: React.FormEvent) {
    e.preventDefault();
    if (!newTerm.trim()) return;

    setAdding(true);
    setError(null);

    try {
      await filtersApi.create(newTerm.trim());
      setNewTerm("");
      loadFilters();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Erro ao adicionar termo");
    } finally {
      setAdding(false);
    }
  }

  async function handleToggleFilter(id: string, currentActive: boolean) {
    try {
      await filtersApi.update(id, { is_active: !currentActive });
      setFilters(
        filters.map((f) =>
          f.id === id ? { ...f, is_active: !currentActive } : f
        )
      );
    } catch (error) {
      console.error("Error toggling filter:", error);
    }
  }

  async function handleDeleteFilter(id: string) {
    if (!confirm("Tem certeza que deseja remover este termo?")) return;

    try {
      await filtersApi.delete(id);
      setFilters(filters.filter((f) => f.id !== id));
      setLimitReached(false);
    } catch (error) {
      console.error("Error deleting filter:", error);
    }
  }

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
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Termos Monitorados</h1>
        <p className="text-gray-500">
          Gerencie os termos que você deseja monitorar na mídia
        </p>
      </div>

      {/* Add Filter Form */}
      <Card>
        <CardHeader>
          <CardTitle>Adicionar Novo Termo</CardTitle>
          <CardDescription>
            Digite o nome, termo ou palavra-chave que deseja monitorar
          </CardDescription>
        </CardHeader>
        <CardContent>
          {error && (
            <div className="mb-4 p-3 rounded-lg bg-red-50 border border-red-200 flex items-center space-x-2 text-red-700">
              <AlertCircle className="w-5 h-5 flex-shrink-0" />
              <span className="text-sm">{error}</span>
            </div>
          )}

          {limitReached && (
            <div className="mb-4 p-4 rounded-lg bg-amber-50 border border-amber-200">
              <div className="flex items-start space-x-3">
                <Crown className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-medium text-amber-800">
                    Limite de termos atingido
                  </p>
                  <p className="text-sm text-amber-700 mt-1">
                    Seu plano permite até {planLimit} termos. Faça upgrade para o
                    plano Pro para monitorar mais termos.
                  </p>
                  <Button
                    variant="secondary"
                    size="sm"
                    className="mt-3 bg-amber-100 hover:bg-amber-200 text-amber-800"
                  >
                    Fazer Upgrade
                  </Button>
                </div>
              </div>
            </div>
          )}

          <form onSubmit={handleAddFilter} className="flex gap-3">
            <div className="flex-1">
              <Input
                value={newTerm}
                onChange={(e) => setNewTerm(e.target.value)}
                placeholder="Ex: João Silva, Projeto de Lei 123, Reforma Tributária..."
                disabled={limitReached}
              />
            </div>
            <Button type="submit" isLoading={adding} disabled={limitReached}>
              <Plus className="w-4 h-4 mr-2" />
              Adicionar
            </Button>
          </form>

          <p className="text-sm text-gray-500 mt-3">
            {filters.length} de {planLimit} termos utilizados
          </p>
        </CardContent>
      </Card>

      {/* Filters List */}
      <Card>
        <CardHeader>
          <CardTitle>Seus Termos</CardTitle>
          <CardDescription>
            {filters.length === 0
              ? "Você ainda não adicionou nenhum termo"
              : `${filters.filter((f) => f.is_active).length} termos ativos`}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {filters.length > 0 ? (
            <div className="space-y-3">
              {filters.map((filter) => (
                <div
                  key={filter.id}
                  className={`flex items-center justify-between p-4 rounded-lg border transition-colors ${
                    filter.is_active
                      ? "bg-white border-gray-200"
                      : "bg-gray-50 border-gray-100"
                  }`}
                >
                  <div className="flex items-center space-x-4">
                    <div
                      className={`w-2 h-2 rounded-full ${
                        filter.is_active ? "bg-green-500" : "bg-gray-400"
                      }`}
                    />
                    <div>
                      <p
                        className={`font-medium ${
                          filter.is_active ? "text-gray-900" : "text-gray-500"
                        }`}
                      >
                        {filter.term}
                      </p>
                      <p className="text-sm text-gray-500">
                        {filter.match_count} menções encontradas
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center space-x-2">
                    <Badge variant={filter.is_active ? "positive" : "default"}>
                      {filter.is_active ? "Ativo" : "Inativo"}
                    </Badge>

                    <button
                      onClick={() => handleToggleFilter(filter.id, filter.is_active)}
                      className={`p-2 rounded-lg transition-colors ${
                        filter.is_active
                          ? "text-amber-600 hover:bg-amber-50"
                          : "text-green-600 hover:bg-green-50"
                      }`}
                      title={filter.is_active ? "Desativar" : "Ativar"}
                    >
                      {filter.is_active ? (
                        <PowerOff className="w-5 h-5" />
                      ) : (
                        <Power className="w-5 h-5" />
                      )}
                    </button>

                    <button
                      onClick={() => handleDeleteFilter(filter.id)}
                      className="p-2 rounded-lg text-red-600 hover:bg-red-50 transition-colors"
                      title="Remover"
                    >
                      <Trash2 className="w-5 h-5" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <Filter className="w-16 h-16 mx-auto mb-4 text-gray-300" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Nenhum termo cadastrado
              </h3>
              <p className="text-gray-500">
                Adicione termos acima para começar a monitorar notícias
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
