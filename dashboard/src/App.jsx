import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
    Activity,
    FileText,
    AlertCircle,
    CheckCircle2,
    Clock,
    Search,
    Filter,
    ExternalLink,
    ChevronRight,
    TrendingUp,
    Package,
    Truck,
    Building2,
    ShoppingCart
} from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const StatusBadge = ({ status }) => {
    const styles = {
        autorizado: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
        error: 'bg-rose-500/10 text-rose-400 border-rose-500/20',
        processing: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
        authorized: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
        denied: 'bg-rose-500/10 text-rose-400 border-rose-500/20',
    };

    const normalized = status?.toLowerCase() || 'processing';
    const style = styles[normalized] || styles.processing;

    return (
        <span className={`px-2 py-1 text-xs font-medium rounded-full border ${style}`}>
            {status?.toUpperCase()}
        </span>
    );
};

const TypeIcon = ({ type }) => {
    switch (type) {
        case 'nfse': return <Building2 size={16} />;
        case 'nfe': return <Package size={16} />;
        case 'nfce': return <ShoppingCart size={16} />;
        case 'cte': return <Truck size={16} />;
        case 'mdfe': return <FileText size={16} />;
        default: return <FileText size={16} />;
    }
};

const TimelineItem = ({ event }) => (
    <div className="relative pl-6 pb-6 border-l border-white/10 last:pb-0">
        <div className="absolute left-[-5px] top-0 w-2 h-2 rounded-full bg-brand-500 shadow-[0_0_8px_rgba(92,122,255,0.6)]" />
        <div className="flex justify-between items-start">
            <div>
                <p className="text-sm font-medium text-slate-200">{event.message}</p>
                <p className="text-xs text-slate-500">{event.status.toUpperCase()}</p>
            </div>
            <span className="text-[10px] text-slate-500 font-mono">
                {new Date(event.created_at).toLocaleTimeString()}
            </span>
        </div>
    </div>
);

export default function App() {
    const [stats, setStats] = useState({});
    const [invoices, setInvoices] = useState([]);
    const [selectedInvoice, setSelectedInvoice] = useState(null);
    const [timeline, setTimeline] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchData();
        const interval = setInterval(fetchData, 10000); // Auto refresh
        return () => clearInterval(interval);
    }, []);

    const fetchData = async () => {
        try {
            const [statsRes, listRes] = await Promise.all([
                axios.get('/nfse/dashboard/stats'),
                axios.get('/nfse/dashboard/list?limit=10')
            ]);
            setStats(statsRes.data);
            setInvoices(listRes.data);
            setLoading(false);
        } catch (err) {
            console.error("Erro ao buscar dados", err);
        }
    };

    const fetchTimeline = async (ref) => {
        try {
            const res = await axios.get(`/nfse/${ref}/timeline`);
            setTimeline(res.data);
        } catch (err) {
            console.error("Erro ao buscar timeline", err);
        }
    };

    const selectInvoice = (invoice) => {
        setSelectedInvoice(invoice);
        fetchTimeline(invoice.referencia);
    };

    const chartData = [
        { name: 'Seg', volume: 45 },
        { name: 'Ter', volume: 52 },
        { name: 'Qua', volume: 48 },
        { name: 'Qui', volume: 61 },
        { name: 'Sex', volume: 55 },
        { name: 'Sab', volume: 20 },
        { name: 'Dom', volume: 15 },
    ];

    return (
        <div className="min-h-screen flex flex-col">
            {/* Header */}
            <header className="glass-header sticky top-0 z-50 px-8 py-4 flex justify-between items-center">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-brand-600 rounded-xl flex items-center justify-center shadow-lg shadow-brand-600/20">
                        <Activity className="text-white" size={24} />
                    </div>
                    <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">
                        Contabil IA <span className="text-brand-400 font-medium">Fiscal Hub</span>
                    </h1>
                </div>

                <div className="flex items-center gap-4">
                    <div className="relative">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={16} />
                        <input
                            type="text"
                            placeholder="Buscar por referência..."
                            className="bg-white/5 border border-white/10 rounded-full py-2 pl-10 pr-4 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500/50 w-64 transition-all"
                        />
                    </div>
                    <div className="w-8 h-8 rounded-full bg-slate-800 border border-white/10 flex items-center justify-center overflow-hidden">
                        <div className="w-2 h-2 rounded-full bg-brand-500 animate-pulse" />
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="flex-1 p-8 grid grid-cols-12 gap-8">

                {/* Left Column: Stats & Chart */}
                <div className="col-span-12 lg:col-span-8 space-y-8">

                    {/* Stats Cards */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <div className="glass p-6 rounded-2xl">
                            <div className="flex justify-between items-start mb-4">
                                <div className="p-2 bg-emerald-500/10 rounded-lg text-emerald-500">
                                    <CheckCircle2 size={24} />
                                </div>
                                <TrendingUp size={16} className="text-emerald-500" />
                            </div>
                            <p className="text-slate-400 text-sm">Autorizadas</p>
                            <p className="text-3xl font-bold">{stats.autorizado || stats.authorized || 0}</p>
                        </div>

                        <div className="glass p-6 rounded-2xl">
                            <div className="flex justify-between items-start mb-4">
                                <div className="p-2 bg-rose-500/10 rounded-lg text-rose-500">
                                    <AlertCircle size={24} />
                                </div>
                            </div>
                            <p className="text-slate-400 text-sm">Erro / Rejeitada</p>
                            <p className="text-3xl font-bold">{stats.error || stats.denied || 0}</p>
                        </div>

                        <div className="glass p-6 rounded-2xl">
                            <div className="flex justify-between items-start mb-4">
                                <div className="p-2 bg-brand-500/10 rounded-lg text-brand-500">
                                    <Clock size={24} />
                                </div>
                            </div>
                            <p className="text-slate-400 text-sm">Processando</p>
                            <p className="text-3xl font-bold">{stats.processing || 0}</p>
                        </div>
                    </div>

                    {/* Chart Section */}
                    <div className="glass p-6 rounded-2xl h-[350px] relative overflow-hidden">
                        <h3 className="text-lg font-semibold mb-6 flex items-center gap-2">
                            <Activity size={18} className="text-brand-500" /> Volume Semanal
                        </h3>
                        <div className="h-[250px] w-full">
                            <ResponsiveContainer width="100%" height="100%">
                                <AreaChart data={chartData}>
                                    <defs>
                                        <linearGradient id="colorVolume" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#5c7aff" stopOpacity={0.3} />
                                            <stop offset="95%" stopColor="#5c7aff" stopOpacity={0} />
                                        </linearGradient>
                                    </defs>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" vertical={false} />
                                    <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 12 }} />
                                    <YAxis hide />
                                    <Tooltip
                                        contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #ffffff10', borderRadius: '8px' }}
                                        itemStyle={{ color: '#f8fafc' }}
                                    />
                                    <Area
                                        type="monotone"
                                        dataKey="volume"
                                        stroke="#5c7aff"
                                        strokeWidth={3}
                                        fillOpacity={1}
                                        fill="url(#colorVolume)"
                                    />
                                </AreaChart>
                            </ResponsiveContainer>
                        </div>
                    </div>

                    {/* Invoices List */}
                    <div className="glass rounded-2xl overflow-hidden">
                        <div className="px-6 py-4 border-b border-white/5 flex justify-between items-center bg-white/5">
                            <h3 className="font-semibold">Últimas Emissões</h3>
                            <button className="text-xs text-brand-400 hover:text-brand-300 flex items-center gap-1 transition-colors">
                                Ver Todas <ChevronRight size={14} />
                            </button>
                        </div>
                        <div className="overflow-x-auto">
                            <table className="w-full text-left">
                                <thead>
                                    <tr className="text-slate-500 text-xs uppercase tracking-wider">
                                        <th className="px-6 py-4 font-medium">Doc</th>
                                        <th className="px-6 py-4 font-medium">Referência</th>
                                        <th className="px-6 py-4 font-medium">Status</th>
                                        <th className="px-6 py-4 font-medium">Data</th>
                                        <th className="px-6 py-4"></th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-white/5">
                                    {invoices.map((inv) => (
                                        <tr
                                            key={inv.id}
                                            onClick={() => selectInvoice(inv)}
                                            className={`hover:bg-brand-500/5 cursor-pointer transition-colors ${selectedInvoice?.id === inv.id ? 'bg-brand-500/10' : ''}`}
                                        >
                                            <td className="px-6 py-4">
                                                <div className="w-8 h-8 rounded-lg bg-slate-800 flex items-center justify-center text-slate-400 border border-white/5">
                                                    <TypeIcon type={inv.type} />
                                                </div>
                                            </td>
                                            <td className="px-6 py-4 font-medium text-sm">{inv.referencia}</td>
                                            <td className="px-6 py-4">
                                                <StatusBadge status={inv.status} />
                                            </td>
                                            <td className="px-6 py-4 text-xs text-slate-500">
                                                {new Date(inv.created_at).toLocaleString()}
                                            </td>
                                            <td className="px-6 py-4 text-right">
                                                <ChevronRight size={16} className="text-slate-700 ml-auto" />
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                {/* Right Column: Details & Timeline */}
                <div className="col-span-12 lg:col-span-4 space-y-8">
                    {selectedInvoice ? (
                        <div className="glass p-6 rounded-2xl sticky top-24">
                            <div className="flex justify-between items-start mb-6">
                                <div>
                                    <h3 className="text-lg font-bold">Resumo da Nota</h3>
                                    <p className="text-xs text-slate-500 uppercase tracking-widest">{selectedInvoice.type}</p>
                                </div>
                                <StatusBadge status={selectedInvoice.status} />
                            </div>

                            <div className="space-y-4 mb-8">
                                <div className="flex justify-between py-2 border-b border-white/5">
                                    <span className="text-sm text-slate-500">Referência</span>
                                    <span className="text-sm font-mono">{selectedInvoice.referencia}</span>
                                </div>
                                <div className="flex justify-between py-2 border-b border-white/5">
                                    <span className="text-sm text-slate-500">External ID</span>
                                    <span className="text-sm font-mono">{selectedInvoice.external_id || '-'}</span>
                                </div>
                                {selectedInvoice.pdf_url && (
                                    <a
                                        href={`/storage/${selectedInvoice.pdf_url}`}
                                        target="_blank"
                                        className="flex items-center justify-center gap-2 w-full py-3 bg-brand-600 hover:bg-brand-500 text-white rounded-xl text-sm font-semibold transition-all shadow-lg shadow-brand-600/20"
                                    >
                                        Visualizar PDF <ExternalLink size={16} />
                                    </a>
                                )}
                            </div>

                            {/* Timeline Section */}
                            <div>
                                <h4 className="text-sm font-bold uppercase tracking-widest text-slate-500 mb-6">Timeline de Eventos</h4>
                                <div className="space-y-0">
                                    {timeline.length > 0 ? (
                                        timeline.map((evt) => <TimelineItem key={evt.id} event={evt} />)
                                    ) : (
                                        <p className="text-sm text-slate-600 italic">Buscando histórico...</p>
                                    )}
                                </div>
                            </div>
                        </div>
                    ) : (
                        <div className="glass p-8 rounded-2xl flex flex-col items-center justify-center text-center h-[400px] border-dashed border-white/10">
                            <div className="w-16 h-16 bg-slate-800/50 rounded-2xl flex items-center justify-center mb-4 text-slate-600">
                                <FileText size={32} />
                            </div>
                            <h3 className="text-lg font-semibold text-slate-400">Nenhuma Nota Selecionada</h3>
                            <p className="text-sm text-slate-600 max-w-[200px]">Clique em uma nota na lista para ver detalhes e timeline.</p>
                        </div>
                    )}
                </div>

            </main>

            {/* Footer */}
            <footer className="p-8 text-center text-slate-600 text-sm">
                &copy; 2025 Contabil IA - Sistema de Gestão Fiscal v2.0.0
            </footer>
        </div>
    );
}
