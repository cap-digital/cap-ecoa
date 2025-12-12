import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuthStore } from "../store/authStore";
import { Button } from "../components/ui/Button";
import { Input } from "../components/ui/Input";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../components/ui/Card";
import { Newspaper, AlertCircle } from "lucide-react";

const ESTADOS = [
  "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA",
  "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN",
  "RS", "RO", "RR", "SC", "SP", "SE", "TO"
];

export function Register() {
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    confirmPassword: "",
    full_name: "",
    political_name: "",
    party: "",
    state: "",
  });
  const [formError, setFormError] = useState("");
  const { register, isLoading, error, clearError } = useAuthStore();
  const navigate = useNavigate();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();
    setFormError("");

    if (formData.password !== formData.confirmPassword) {
      setFormError("As senhas não coincidem");
      return;
    }

    if (formData.password.length < 6) {
      setFormError("A senha deve ter pelo menos 6 caracteres");
      return;
    }

    try {
      await register({
        email: formData.email,
        password: formData.password,
        full_name: formData.full_name,
        political_name: formData.political_name || undefined,
        party: formData.party || undefined,
        state: formData.state || undefined,
      });
      navigate("/dashboard");
    } catch (err) {
      // Error is handled in store
    }
  };

  const displayError = formError || error;

  return (
    <Card className="w-full max-w-md">
      <CardHeader className="text-center">
        <div className="flex justify-center mb-4">
          <div className="w-12 h-12 bg-primary-600 rounded-xl flex items-center justify-center">
            <Newspaper className="w-7 h-7 text-white" />
          </div>
        </div>
        <CardTitle className="text-2xl">Criar Conta</CardTitle>
        <CardDescription>
          Cadastre-se para monitorar suas menções na mídia
        </CardDescription>
      </CardHeader>

      <CardContent>
        {displayError && (
          <div className="mb-4 p-3 rounded-lg bg-red-50 border border-red-200 flex items-center space-x-2 text-red-700">
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
            <span className="text-sm">{displayError}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            label="Nome Completo"
            name="full_name"
            value={formData.full_name}
            onChange={handleChange}
            placeholder="Seu nome completo"
            required
          />

          <Input
            label="Email"
            type="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            placeholder="seu@email.com"
            required
          />

          <div className="grid grid-cols-2 gap-4">
            <Input
              label="Senha"
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="******"
              required
            />
            <Input
              label="Confirmar Senha"
              type="password"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
              placeholder="******"
              required
            />
          </div>

          <div className="border-t border-gray-200 pt-4 mt-4">
            <p className="text-sm text-gray-500 mb-3">Informações políticas (opcional)</p>

            <Input
              label="Nome Político"
              name="political_name"
              value={formData.political_name}
              onChange={handleChange}
              placeholder="Como é conhecido na política"
            />

            <div className="grid grid-cols-2 gap-4 mt-4">
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
          </div>

          <Button
            type="submit"
            className="w-full"
            isLoading={isLoading}
          >
            Criar Conta
          </Button>
        </form>

        <div className="mt-6 text-center">
          <p className="text-sm text-gray-600">
            Já tem uma conta?{" "}
            <Link
              to="/login"
              className="text-primary-600 hover:text-primary-700 font-medium"
            >
              Fazer login
            </Link>
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
