import { useState } from "react";
import { useAuthStore } from "../store/authStore";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../components/ui/Card";
import { Button } from "../components/ui/Button";
import { Input } from "../components/ui/Input";
import { Badge } from "../components/ui/Badge";
import {
  User,
  Crown,
  CheckCircle,
  AlertCircle,
} from "lucide-react";

const ESTADOS = [
  "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA",
  "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN",
  "RS", "RO", "RR", "SC", "SP", "SE", "TO"
];

export function SettingsPage() {
  const { user, updateUser, isLoading } = useAuthStore();
  const [formData, setFormData] = useState({
    full_name: user?.full_name || "",
    political_name: user?.political_name || "",
    party: user?.party || "",
    state: user?.state || "",
  });
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    setSuccess(false);
    setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(false);

    try {
      await updateUser(formData);
      setSuccess(true);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Erro ao atualizar perfil");
    }
  };

  const planFeatures = {
    free: [
      "Até 3 termos monitorados",
      "Notícias dos últimos 7 dias",
      "2 fontes de notícias",
      "Análise de sentimento básica",
    ],
    pro: [
      "Até 100 termos monitorados",
      "Histórico completo de notícias",
      "Todas as fontes de notícias",
      "Análise de sentimento avançada",
      "Alertas por email",
      "Relatórios em PDF",
      "Suporte prioritário",
    ],
  };

  return (
    <div className="space-y-6 max-w-3xl">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Configurações</h1>
        <p className="text-gray-500">Gerencie seu perfil e plano</p>
      </div>

      {/* Profile Card */}
      <Card>
        <CardHeader>
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center">
              <User className="w-6 h-6 text-primary-600" />
            </div>
            <div>
              <CardTitle>Informações do Perfil</CardTitle>
              <CardDescription>
                Atualize suas informações pessoais
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {success && (
            <div className="mb-4 p-3 rounded-lg bg-green-50 border border-green-200 flex items-center space-x-2 text-green-700">
              <CheckCircle className="w-5 h-5 flex-shrink-0" />
              <span className="text-sm">Perfil atualizado com sucesso!</span>
            </div>
          )}

          {error && (
            <div className="mb-4 p-3 rounded-lg bg-red-50 border border-red-200 flex items-center space-x-2 text-red-700">
              <AlertCircle className="w-5 h-5 flex-shrink-0" />
              <span className="text-sm">{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input
                label="Nome Completo"
                name="full_name"
                value={formData.full_name}
                onChange={handleChange}
              />
              <Input
                label="Nome Político"
                name="political_name"
                value={formData.political_name}
                onChange={handleChange}
                placeholder="Como é conhecido na política"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input
                label="Partido"
                name="party"
                value={formData.party}
                onChange={handleChange}
                placeholder="Ex: PT, PSDB..."
              />

              <div className="w-full">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Estado
                </label>
                <select
                  name="state"
                  value={formData.state}
                  onChange={handleChange}
                  className="w-full rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500"
                >
                  <option value="">Selecione</option>
                  {ESTADOS.map((uf) => (
                    <option key={uf} value={uf}>{uf}</option>
                  ))}
                </select>
              </div>
            </div>

            <div className="pt-4">
              <Button type="submit" isLoading={isLoading}>
                Salvar Alterações
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      {/* Plan Card */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-amber-100 rounded-full flex items-center justify-center">
                <Crown className="w-6 h-6 text-amber-600" />
              </div>
              <div>
                <CardTitle>Seu Plano</CardTitle>
                <CardDescription>
                  Gerencie sua assinatura
                </CardDescription>
              </div>
            </div>
            <Badge
              variant={user?.plan_type === "pro" ? "positive" : "default"}
              className="text-sm px-3 py-1"
            >
              {user?.plan_type === "pro" ? "PRO" : "FREE"}
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Free Plan */}
            <div
              className={`p-6 rounded-xl border-2 ${
                user?.plan_type === "free"
                  ? "border-primary-500 bg-primary-50"
                  : "border-gray-200"
              }`}
            >
              <h3 className="text-lg font-semibold mb-2">Plano Free</h3>
              <p className="text-2xl font-bold mb-4">
                R$ 0<span className="text-sm font-normal text-gray-500">/mês</span>
              </p>
              <ul className="space-y-2">
                {planFeatures.free.map((feature) => (
                  <li key={feature} className="flex items-center text-sm text-gray-600">
                    <CheckCircle className="w-4 h-4 text-green-500 mr-2 flex-shrink-0" />
                    {feature}
                  </li>
                ))}
              </ul>
              {user?.plan_type === "free" && (
                <Badge variant="neutral" className="mt-4">
                  Plano Atual
                </Badge>
              )}
            </div>

            {/* Pro Plan */}
            <div
              className={`p-6 rounded-xl border-2 ${
                user?.plan_type === "pro"
                  ? "border-primary-500 bg-primary-50"
                  : "border-gray-200"
              }`}
            >
              <h3 className="text-lg font-semibold mb-2">Plano Pro</h3>
              <p className="text-2xl font-bold mb-4">
                R$ 99<span className="text-sm font-normal text-gray-500">/mês</span>
              </p>
              <ul className="space-y-2">
                {planFeatures.pro.map((feature) => (
                  <li key={feature} className="flex items-center text-sm text-gray-600">
                    <CheckCircle className="w-4 h-4 text-green-500 mr-2 flex-shrink-0" />
                    {feature}
                  </li>
                ))}
              </ul>
              {user?.plan_type === "pro" ? (
                <Badge variant="positive" className="mt-4">
                  Plano Atual
                </Badge>
              ) : (
                <Button className="mt-4 w-full">
                  Fazer Upgrade
                </Button>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Account Info */}
      <Card>
        <CardHeader>
          <CardTitle>Informações da Conta</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex justify-between py-2 border-b border-gray-100">
              <span className="text-gray-500">Email</span>
              <span className="font-medium">{user?.email}</span>
            </div>
            <div className="flex justify-between py-2 border-b border-gray-100">
              <span className="text-gray-500">ID da conta</span>
              <span className="font-mono text-sm">{user?.id?.slice(0, 8)}...</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
