import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import { DataGrid } from '@mui/x-data-grid';

// 일일 방문자 데이터 예시
const visitData = [
  { date: '2024-03-01', visitors: 15 },
  { date: '2024-03-02', visitors: 20 },
  { date: '2024-03-03', visitors: 25 },
  { date: '2024-03-04', visitors: 18 },
  { date: '2024-03-05', visitors: 30 },
];

// 그리드 컬럼 정의
const columns = [
  { field: 'id', headerName: 'NO.', width: 90 },
  { field: 'name', headerName: '이름', width: 130 },
  { field: 'phone', headerName: '전화번호', width: 180 },
  { field: 'account', headerName: '계좌번호', width: 200 },
];

export function Dashboard() {
  return (
    <div className="dashboard-container">
      <div className="chart-container">
        <h2>일일 방문자 현황</h2>
        <BarChart width={800} height={300} data={visitData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="visitors" fill="#8884d8" />
        </BarChart>
      </div>
      
      <div className="grid-container">
        <h2>오늘의 방문자 목록</h2>
        <div style={{ height: 400, width: '100%' }}>
          <DataGrid
            rows={[]}  // 실제 데이터로 교체 필요
            columns={columns}
            pageSize={5}
            rowsPerPageOptions={[5]}
            checkboxSelection
            disableSelectionOnClick
          />
        </div>
      </div>
    </div>
  );
} 