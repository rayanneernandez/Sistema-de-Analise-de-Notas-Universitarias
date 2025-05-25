import React, { useState, useEffect } from 'react';
import { GraduationCap, Users, BookOpen, FileBarChart, Upload, LogOut } from 'lucide-react';

interface DashboardData {
  total_students: number;
  total_courses: number;
  average_grade: number;
  at_risk_count: number;
  grade_distribution: {
    labels: string[];
    data: number[];
  };
  department_performance: {
    labels: string[];
    data: number[];
  };
}

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);

  useEffect(() => {
    if (activeTab === 'dashboard') {
      fetch('/api/dashboard')
        .then(response => response.json())
        .then(data => setDashboardData(data))
        .catch(error => console.error('Erro ao buscar dados do painel:', error));
    }
  }, [activeTab]);

  return (
    <div className="min-h-screen bg-gray-100 flex">
      {/* Barra lateral */}
      <div className="w-64 bg-[#1a3a6c] text-white">
        <div className="p-6 border-b border-white/10">
          <h4 className="flex items-center text-xl font-semibold">
            <GraduationCap className="mr-2" />
            Sistema de Notas
          </h4>
        </div>
        <nav className="p-4">
          <button
            onClick={() => setActiveTab('dashboard')}
            className={`w-full flex items-center p-3 rounded-lg mb-2 ${
              activeTab === 'dashboard' ? 'bg-white/20 border-l-4 border-[#f8a01c]' : 'hover:bg-white/10'
            }`}
          >
            <GraduationCap className="mr-3" size={20} />
            Painel Principal
          </button>
          <button
            onClick={() => setActiveTab('students')}
            className={`w-full flex items-center p-3 rounded-lg mb-2 ${
              activeTab === 'students' ? 'bg-white/20 border-l-4 border-[#f8a01c]' : 'hover:bg-white/10'
            }`}
          >
            <Users className="mr-3" size={20} />
            Alunos
          </button>
          <button
            onClick={() => setActiveTab('courses')}
            className={`w-full flex items-center p-3 rounded-lg mb-2 ${
              activeTab === 'courses' ? 'bg-white/20 border-l-4 border-[#f8a01c]' : 'hover:bg-white/10'
            }`}
          >
            <BookOpen className="mr-3" size={20} />
            Disciplinas
          </button>
          <button
            onClick={() => setActiveTab('reports')}
            className={`w-full flex items-center p-3 rounded-lg mb-2 ${
              activeTab === 'reports' ? 'bg-white/20 border-l-4 border-[#f8a01c]' : 'hover:bg-white/10'
            }`}
          >
            <FileBarChart className="mr-3" size={20} />
            Relatórios
          </button>
          <button
            onClick={() => setActiveTab('upload')}
            className={`w-full flex items-center p-3 rounded-lg mb-2 ${
              activeTab === 'upload' ? 'bg-white/20 border-l-4 border-[#f8a01c]' : 'hover:bg-white/10'
            }`}
          >
            <Upload className="mr-3" size={20} />
            Importar Dados
          </button>
          <button
            onClick={() => window.location.href = '/logout'}
            className="w-full flex items-center p-3 rounded-lg mt-8 hover:bg-white/10 text-red-300"
          >
            <LogOut className="mr-3" size={20} />
            Sair
          </button>
        </nav>
      </div>

      {/* Conteúdo Principal */}
      <div className="flex-1 p-8">
        <div className="max-w-7xl mx-auto">
          {activeTab === 'dashboard' && (
            <div>
              <h1 className="text-3xl font-bold mb-8">Painel Principal</h1>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                <StatCard 
                  title="Total de Alunos" 
                  value={dashboardData?.total_students.toString() || '0'} 
                  icon={<Users size={24} />} 
                  color="bg-blue-500" 
                />
                <StatCard 
                  title="Total de Disciplinas" 
                  value={dashboardData?.total_courses.toString() || '0'} 
                  icon={<BookOpen size={24} />} 
                  color="bg-green-500" 
                />
                <StatCard 
                  title="Média Geral" 
                  value={dashboardData?.average_grade.toFixed(1) || '0.0'} 
                  icon={<GraduationCap size={24} />} 
                  color="bg-yellow-500" 
                />
                <StatCard 
                  title="Alunos em Risco" 
                  value={dashboardData?.at_risk_count.toString() || '0'} 
                  icon={<Users size={24} />} 
                  color="bg-red-500" 
                />
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-white p-6 rounded-lg shadow">
                  <h2 className="text-xl font-semibold mb-4">Distribuição de Notas</h2>
                  {dashboardData?.grade_distribution ? (
                    <div className="h-64">
                      <pre className="text-sm">{JSON.stringify(dashboardData.grade_distribution, null, 2)}</pre>
                    </div>
                  ) : (
                    <div className="h-64 flex items-center justify-center text-gray-400">
                      Carregando dados...
                    </div>
                  )}
                </div>
                <div className="bg-white p-6 rounded-lg shadow">
                  <h2 className="text-xl font-semibold mb-4">Desempenho por Departamento</h2>
                  {dashboardData?.department_performance ? (
                    <div className="h-64">
                      <pre className="text-sm">{JSON.stringify(dashboardData.department_performance, null, 2)}</pre>
                    </div>
                  ) : (
                    <div className="h-64 flex items-center justify-center text-gray-400">
                      Carregando dados...
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
          {activeTab === 'students' && (
            <div>
              <h1 className="text-3xl font-bold mb-8">Alunos</h1>
              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center justify-between mb-6">
                  <div className="relative">
                    <input
                      type="text"
                      placeholder="Pesquisar alunos..."
                      className="pl-10 pr-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <Users className="absolute left-3 top-2.5 text-gray-400" size={20} />
                  </div>
                  <button className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition-colors">
                    Adicionar Aluno
                  </button>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left py-3 px-4">Matrícula</th>
                        <th className="text-left py-3 px-4">Nome</th>
                        <th className="text-left py-3 px-4">Departamento</th>
                        <th className="text-left py-3 px-4">CR</th>
                        <th className="text-left py-3 px-4">Ações</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr className="text-gray-400 text-center">
                        <td colSpan={5} className="py-8">Nenhum aluno encontrado</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}
          {activeTab === 'courses' && (
            <div>
              <h1 className="text-3xl font-bold mb-8">Disciplinas</h1>
              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center justify-between mb-6">
                  <div className="relative">
                    <input
                      type="text"
                      placeholder="Pesquisar disciplinas..."
                      className="pl-10 pr-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <BookOpen className="absolute left-3 top-2.5 text-gray-400" size={20} />
                  </div>
                  <button className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition-colors">
                    Adicionar Disciplina
                  </button>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left py-3 px-4">Código</th>
                        <th className="text-left py-3 px-4">Nome</th>
                        <th className="text-left py-3 px-4">Departamento</th>
                        <th className="text-left py-3 px-4">Créditos</th>
                        <th className="text-left py-3 px-4">Ações</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr className="text-gray-400 text-center">
                        <td colSpan={5} className="py-8">Nenhuma disciplina encontrada</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}
          {activeTab === 'reports' && (
            <div>
              <h1 className="text-3xl font-bold mb-8">Relatórios</h1>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <ReportCard
                  title="Distribuição de Notas"
                  description="Visualize a distribuição de notas por disciplina e departamento"
                  icon={<FileBarChart size={24} />}
                />
                <ReportCard
                  title="Desempenho por Departamento"
                  description="Compare métricas de desempenho entre departamentos"
                  icon={<Users size={24} />}
                />
                <ReportCard
                  title="Tendências por Disciplina"
                  description="Analise tendências de notas ao longo dos períodos"
                  icon={<BookOpen size={24} />}
                />
              </div>
            </div>
          )}
          {activeTab === 'upload' && (
            <div>
              <h1 className="text-3xl font-bold mb-8">Importar Dados</h1>
              <div className="bg-white rounded-lg shadow p-6">
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
                  <Upload className="mx-auto text-gray-400 mb-4" size={48} />
                  <h3 className="text-lg font-semibold mb-2">Importar Notas</h3>
                  <p className="text-gray-500 mb-4">Arraste e solte seu arquivo CSV ou Excel aqui, ou clique para selecionar</p>
                  <button className="bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600 transition-colors">
                    Selecionar Arquivo
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function StatCard({ title, value, icon, color }: { title: string; value: string; icon: React.ReactNode; color: string }) {
  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <div className="flex items-center">
        <div className={`${color} p-3 rounded-lg text-white mr-4`}>
          {icon}
        </div>
        <div>
          <h3 className="text-gray-500 text-sm">{title}</h3>
          <p className="text-2xl font-semibold">{value}</p>
        </div>
      </div>
    </div>
  );
}

function ReportCard({ title, description, icon }: { title: string; description: string; icon: React.ReactNode }) {
  return (
    <div className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition-shadow cursor-pointer">
      <div className="bg-blue-100 text-blue-500 p-3 rounded-lg w-fit mb-4">
        {icon}
      </div>
      <h3 className="text-lg font-semibold mb-2">{title}</h3>
      <p className="text-gray-500">{description}</p>
    </div>
  );
}

export default App;