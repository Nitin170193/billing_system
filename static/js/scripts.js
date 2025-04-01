
<script>
    // Toggle Sidebar for Mobile
    document.getElementById('toggleSidebar').addEventListener('click', function() {
        document.getElementById('sidebar').classList.toggle('collapsed');
        document.getElementById('main-content').classList.toggle('expanded');
    });
</script>


    <script>
        var ctx = document.getElementById('salesChart').getContext('2d');
        var salesChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Total Sales', 'Sales Return', 'GST Return', 'Net Sales'],
                datasets: [{
                    label: 'Amount (₹)',
                    data: [{{ total_sales }}, {{ total_sales_return }}, {{ total_gst_return }}, {{ net_sales }}],
                    backgroundColor: ['blue', 'red', 'yellow', 'green']
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });

        var monthlyCtx = document.getElementById('monthlySalesChart').getContext('2d');
        var monthlySalesChart = new Chart(monthlyCtx, {
            type: 'line',
            data: {
                labels: {{ months|safe }},
                datasets: [
                    {
                        label: 'Monthly Sales (₹)',
                        data: {{ monthly_sales|safe }},
                        borderColor: 'blue',
                        backgroundColor: 'rgba(0, 0, 255, 0.2)',
                        fill: true
                    },
                    {
                        label: 'Monthly Sales Return (₹)',
                        data: {{ monthly_returns|safe }},
                        borderColor: 'red',
                        backgroundColor: 'rgba(255, 0, 0, 0.2)',
                        fill: true
                    }
                ]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    </script>