
        $(document).ready(function() {
            // Fetch ward data
            $.ajax({
                url: 'https://handel.pythonanywhere.com/evaluation3', // Update this URL if needed
                method: 'GET',
                dataType: 'json',
                success: function(data) {
                    console.log('Data received:', data); // Debugging line

                    if (!Array.isArray(data)) {
                        console.error('Expected an array but got:', data);
                        return;
                    }

                    var labels = data.map(item => 'Ward ' + item.ward_id);
                    var totalScores = data.map(item => item.total_score);

                    // Calculate fractions of each statistic relative to total score
                    var fractions = data.map(item => {
                        var total = item.project_completion + item.completion_percentage + item.initiative + item.proposal_success + item.project_awareness + item.effective_communication + item.impact_on_the_community + item.public_participation + item.project_management + item.budget_allocation_awareness + item.financial_management + item.infrastructure_development + item.sustainability + item.inclusivity + item.impact_on_specific_demographics;
                        return {
                            project_completion: (item.project_completion / total) * 100,
                            completion_percentage: (item.completion_percentage / total) * 100,
                            initiative: (item.initiative / total) * 100,
                            proposal_success: (item.proposal_success / total) * 100,
                            project_awareness: (item.project_awareness / total) * 100,
                            effective_communication: (item.effective_communication / total) * 100,
                            impact_on_the_community: (item.impact_on_the_community / total) * 100,
                            public_participation: (item.public_participation / total) * 100,
                            project_management: (item.project_management / total) * 100,
                            budget_allocation_awareness: (item.budget_allocation_awareness / total) * 100,
                            financial_management: (item.financial_management / total) * 100,
                            infrastructure_development: (item.infrastructure_development / total) * 100,
                            sustainability: (item.sustainability / total) * 100,
                            inclusivity: (item.inclusivity / total) * 100,
                            impact_on_specific_demographics: (item.impact_on_specific_demographics / total) * 100,
                            total_score: item.total_score
                        };
                    });

                    console.log('Fractions:', fractions); // Debugging line

                    // Create datasets
                    var datasets = [
                        {
                            label: 'Project Completion',
                            data: fractions.map(f => f.project_completion),
                            backgroundColor: 'rgba(255, 99, 132, 0.2)',
                            borderColor: 'rgba(255, 99, 132, 1)',
                            borderWidth: 1
                        },
                        {
                            label: 'Completion Percentage',
                            data: fractions.map(f => f.completion_percentage),
                            backgroundColor: 'rgba(54, 162, 235, 0.2)',
                            borderColor: 'rgba(54, 162, 235, 1)',
                            borderWidth: 1
                        },
                        {
                            label: 'Initiative',
                            data: fractions.map(f => f.initiative),
                            backgroundColor: 'rgba(255, 206, 86, 0.2)',
                            borderColor: 'rgba(255, 206, 86, 1)',
                            borderWidth: 1
                        },
                        {
                            label: 'Proposal Success',
                            data: fractions.map(f => f.proposal_success),
                            backgroundColor: 'rgba(75, 192, 192, 0.2)',
                            borderColor: 'rgba(75, 192, 192, 1)',
                            borderWidth: 1
                        },
                        {
                            label: 'Project Awareness',
                            data: fractions.map(f => f.project_awareness),
                            backgroundColor: 'rgba(153, 102, 255, 0.2)',
                            borderColor: 'rgba(153, 102, 255, 1)',
                            borderWidth: 1
                        },
                        {
                            label: 'Effective Communication',
                            data: fractions.map(f => f.effective_communication),
                            backgroundColor: 'rgba(255, 159, 64, 0.2)',
                            borderColor: 'rgba(255, 159, 64, 1)',
                            borderWidth: 1
                        },
                        {
                            label: 'Impact on the Community',
                            data: fractions.map(f => f.impact_on_the_community),
                            backgroundColor: 'rgba(199, 199, 199, 0.2)',
                            borderColor: 'rgba(199, 199, 199, 1)',
                            borderWidth: 1
                        },
                        {
                            label: 'Public Participation',
                            data: fractions.map(f => f.public_participation),
                            backgroundColor: 'rgba(83, 102, 255, 0.2)',
                            borderColor: 'rgba(83, 102, 255, 1)',
                            borderWidth: 1
                        },
                        {
                            label: 'Project Management',
                            data: fractions.map(f => f.project_management),
                            backgroundColor: 'rgba(255, 99, 132, 0.2)',
                            borderColor: 'rgba(255, 99, 132, 1)',
                            borderWidth: 1
                        },
                        {
                            label: 'Budget Allocation Awareness',
                            data: fractions.map(f => f.budget_allocation_awareness),
                            backgroundColor: 'rgba(54, 162, 235, 0.2)',
                            borderColor: 'rgba(54, 162, 235, 1)',
                            borderWidth: 1
                        },
                        {
                            label: 'Financial Management',
                            data: fractions.map(f => f.financial_management),
                            backgroundColor: 'rgba(255, 206, 86, 0.2)',
                            borderColor: 'rgba(255, 206, 86, 1)',
                            borderWidth: 1
                        },
                        {
                            label: 'Infrastructure Development',
                            data: fractions.map(f => f.infrastructure_development),
                            backgroundColor: 'rgba(75, 192, 192, 0.2)',
                            borderColor: 'rgba(75, 192, 192, 1)',
                            borderWidth: 1
                        },
                        {
                            label: 'Sustainability',
                            data: fractions.map(f => f.sustainability),
                            backgroundColor: 'rgba(153, 102, 255, 0.2)',
                            borderColor: 'rgba(153, 102, 255, 1)',
                            borderWidth: 1
                        },
                        {
                            label: 'Inclusivity',
                            data: fractions.map(f => f.inclusivity),
                            backgroundColor: 'rgba(255, 159, 64, 0.2)',
                            borderColor: 'rgba(255, 159, 64, 1)',
                            borderWidth: 1
                        },
                        {
                            label: 'Impact on Specific Demographics',
                            data: fractions.map(f => f.impact_on_specific_demographics),
                            backgroundColor: 'rgba(199, 199, 199, 0.2)',
                            borderColor: 'rgba(199, 199, 199, 1)',
                            borderWidth: 1
                        }
                    ];

                    // Create a chart
                    var ctx = document.getElementById('myChart').getContext('2d');
                    var myChart = new Chart(ctx, {
                        type: 'bar',
                        data: {
                            labels: labels,
                            datasets: datasets
                        },
                        options: {
                            scales: {
                                x: {
                                    stacked: true,
                                    title: {
                                        display: true,
                                        text: 'County ID'
                                    }
                                },
                                y: {
                                    stacked: true,
                                    beginAtZero: true,
                                    suggestedMax: 100,
                                    title: {
                                        display: true,
                                        text: 'Percentage (%)'
                                    }
                                }
                            },
                            plugins: {
                                tooltip: {
                                    callbacks: {
                                        label: function(context) {
                                            var label = context.dataset.label || '';
                                            var value = context.raw;
                                            return label + ': ' + value.toFixed(2) + '%';
                                        }
                                    }
                                },
                                legend: {
                                    display: true,
                                    position: 'bottom',
                                    labels: {
                                        boxWidth: 20,
                                        usePointStyle: true
                                    }
                                }
                            },
                            responsive: true,
                            maintainAspectRatio: false,
                            barPercentage: 0.5,
                            categoryPercentage: 0.8
                        }
                    });
                },
                error: function(error) {
                    console.log('Error:', error);
                }
            });

            // Commented out the county data fetching part

            // Fetch county data
            $.ajax({
                url: 'https://handel.pythonanywhere.com/evaluation4', // Update this URL if needed
                method: 'GET',
                dataType: 'json',
                success: function(data) {
                    var labels = data.map(item => 'County ' + item.county_id);
                    var totalScores = data.map(item => item.total_score);

                    // Calculate fractions of each statistic relative to total score
                    var fractions = data.map(item => {
                        var total = item.project_completion + item.completion_percentage + item.initiative + item.proposal_success + item.project_awareness + item.effective_communication + item.impact_on_the_community + item.public_participation + item.project_management + item.budget_allocation_awareness + item.financial_management + item.infrastructure_development + item.sustainability + item.inclusivity + item.impact_on_specific_demographics;
                        return {
                            project_completion: (item.project_completion / total) * 100,
                            completion_percentage: (item.completion_percentage / total) * 100,
                            initiative: (item.initiative / total) * 100,
                            proposal_success: (item.proposal_success / total) * 100,
                            project_awareness: (item.project_awareness / total) * 100,
                            effective_communication: (item.effective_communication / total) * 100,
                            impact_on_the_community: (item.impact_on_the_community / total) * 100,
                            public_participation: (item.public_participation / total) * 100,
                            project_management: (item.project_management / total) * 100,
                            budget_allocation_awareness: (item.budget_allocation_awareness / total) * 100,
                            financial_management: (item.financial_management / total) * 100,
                            infrastructure_development: (item.infrastructure_development / total) * 100,
                            sustainability: (item.sustainability / total) * 100,
                            inclusivity: (item.inclusivity / total) * 100,
                            impact_on_specific_demographics: (item.impact_on_specific_demographics / total) * 100,
                            total_score: item.total_score
                        };
                    });

                    // Create datasets
                    var countyDatasets = [

                        // Similar to the above datasets, but for counties
                        {
                            label: 'Project Completion',
                            data: fractions.map(f => f.project_completion),
                            backgroundColor: 'rgba(255, 99, 132, 0.2)',
                            borderColor: 'rgba(255, 99, 132, 1)',
                            borderWidth: 1
                        },
                        {
                            label: 'Completion Percentage',
                            data: fractions.map(f => f.completion_percentage),
                            backgroundColor: 'rgba(54, 162, 235, 0.2)',
                            borderColor: 'rgba(54, 162, 235, 1)',
                            borderWidth: 1
                        },
                        {
                            label: 'Initiative',
                            data: fractions.map(f => f.initiative),
                            backgroundColor: 'rgba(255, 206, 86, 0.2)',
                            borderColor: 'rgba(255, 206, 86, 1)',
                            borderWidth: 1
                        },
                        {
                            label: 'Proposal Success',
                            data: fractions.map(f => f.proposal_success),
                            backgroundColor: 'rgba(75, 192, 192, 0.2)',
                            borderColor: 'rgba(75, 192, 192, 1)',
                            borderWidth: 1
                        },
                        {
                            label: 'Project Awareness',
                            data: fractions.map(f => f.project_awareness),
                            backgroundColor: 'rgba(153, 102, 255, 0.2)',
                            borderColor: 'rgba(153, 102, 255, 1)',
                            borderWidth: 1
                        },
                        {
                            label: 'Effective Communication',
                            data: fractions.map(f => f.effective_communication),
                            backgroundColor: 'rgba(255, 159, 64, 0.2)',
                            borderColor: 'rgba(255, 159, 64, 1)',
                            borderWidth: 1
                        },
                        {
                            label: 'Impact on the Community',
                            data: fractions.map(f => f.impact_on_the_community),
                            backgroundColor: 'rgba(199, 199, 199, 0.2)',
                            borderColor: 'rgba(199, 199, 199, 1)',
                            borderWidth: 1
                        },
                        {
                            label: 'Public Participation',
                            data: fractions.map(f => f.public_participation),
                            backgroundColor: 'rgba(83, 102, 255, 0.2)',
                            borderColor: 'rgba(83, 102, 255, 1)',
                            borderWidth: 1
                        },
                        {
                            label: 'Project Management',
                            data: fractions.map(f => f.project_management),
                            backgroundColor: 'rgba(255, 99, 132, 0.2)',
                            borderColor: 'rgba(255, 99, 132, 1)',
                            borderWidth: 1
                        },
                        {
                            label: 'Budget Allocation Awareness',
                            data: fractions.map(f => f.budget_allocation_awareness),
                            backgroundColor: 'rgba(54, 162, 235, 0.2)',
                            borderColor: 'rgba(54, 162, 235, 1)',
                            borderWidth: 1
                        },
                        {
                            label: 'Financial Management',
                            data: fractions.map(f => f.financial_management),
                            backgroundColor: 'rgba(255, 206, 86, 0.2)',
                            borderColor: 'rgba(255, 206, 86, 1)',
                            borderWidth: 1
                        },
                        {
                            label: 'Infrastructure Development',
                            data: fractions.map(f => f.infrastructure_development),
                            backgroundColor: 'rgba(75, 192, 192, 0.2)',
                            borderColor: 'rgba(75, 192, 192, 1)',
                            borderWidth: 1
                        },
                        {
                            label: 'Sustainability',
                            data: fractions.map(f => f.sustainability),
                            backgroundColor: 'rgba(153, 102, 255, 0.2)',
                            borderColor: 'rgba(153, 102, 255, 1)',
                            borderWidth: 1
                        },
                        {
                            label: 'Inclusivity',
                            data: fractions.map(f => f.inclusivity),
                            backgroundColor: 'rgba(255, 159, 64, 0.2)',
                            borderColor: 'rgba(255, 159, 64, 1)',
                            borderWidth: 1
                        },
                        {
                            label: 'Impact on Specific Demographics',
                            data: fractions.map(f => f.impact_on_specific_demographics),
                            backgroundColor: 'rgba(199, 199, 199, 0.2)',
                            borderColor: 'rgba(199, 199, 199, 1)',
                            borderWidth: 1
                        }
                    ];

                    // Create a county chart
                    var countyCtx = document.getElementById('countyChart').getContext('2d');
                    var countyChart = new Chart(countyCtx, {
                        type: 'bar',
                        data: {
                            labels: labels,
                            datasets: countyDatasets
                        },
                        options: {
                            scales: {
                                x: {
                                    stacked: true,
                                    title: {
                                        display: true,
                                        text: 'County ID'
                                    }
                                },
                                y: {
                                    stacked: true,
                                    beginAtZero: true,
                                    suggestedMax: 100,
                                    title: {
                                        display: true,
                                        text: 'Percentage (%)'
                                    }
                                }
                            },
                            plugins: {
                                tooltip: {
                                    callbacks: {
                                        label: function(context) {
                                            var label = context.dataset.label || '';
                                            var value = context.raw;
                                            return label + ': ' + value.toFixed(2) + '%';
                                        }
                                    }
                                },
                                legend: {
                                    display: true,
                                    position: 'bottom',
                                    labels: {
                                        boxWidth: 20,
                                        usePointStyle: true
                                    }
                                }
                            },
                            responsive: true,
                            maintainAspectRatio: false,
                            barPercentage: 0.5,
                            categoryPercentage: 0.8
                        }
                    });
                },
                error: function(error) {
                    console.log('Error:', error);
                }
            });

        });
        $(document).ready(function () {
            $('#reportsTable').DataTable({
                "ajax": {
                    "url": "/cgi-bin/scheduledreports.py",
                    "type": "POST",
                    "data": function (d) {
                        d.session_id = getCookie('session_id');
                    },
                    "dataSrc": function (json) {
                        console.log("AJAX Response:", json); // Debugging
                        return json.data || []; // Ensure it returns an array
                    }
                },
                "columns": [
                    { "data": "project_name", "title": "Project Name" },
                    { "data": "status", "title": "Status" },
                    { "data": "date", "title": "Date" }
                ]
            });
        });
