import { AreaChart, Area, ResponsiveContainer, Tooltip, XAxis } from 'recharts';

export default function RevenueChart({ data }) {
  return (
    <ResponsiveContainer width="100%" height={120}>
      <AreaChart data={data} margin={{ top: 8, right: 0, bottom: 0, left: 0 }}>
        <defs>
          <linearGradient id="revenueFill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#4fa490" stopOpacity={0.35} />
            <stop offset="100%" stopColor="#4fa490" stopOpacity={0} />
          </linearGradient>
        </defs>
        <XAxis dataKey="date" hide />
        <Tooltip
          contentStyle={{
            background: '#1d2333',
            border: '1px solid #2a3142',
            borderRadius: 6,
            fontSize: 12,
            fontFamily: 'Inter, sans-serif',
          }}
          labelStyle={{ color: '#8890a3' }}
          itemStyle={{ color: '#ecebe4' }}
          formatter={(value) => [`$${value.toLocaleString()}`, 'Revenue']}
        />
        <Area
          type="monotone"
          dataKey="revenue"
          stroke="#4fa490"
          strokeWidth={2}
          fill="url(#revenueFill)"
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
