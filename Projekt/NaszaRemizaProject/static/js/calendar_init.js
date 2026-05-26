document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('calendar');
    
    var wyjazdyData = JSON.parse(document.getElementById('wyjazdy-data').textContent);
    var pojazdyData = JSON.parse(document.getElementById('pojazdy-data').textContent);
    var strazacyData = JSON.parse(document.getElementById('strazacy-data').textContent);
    var wydarzeniaData = JSON.parse(document.getElementById('wydarzenia-data').textContent);

    var eventList = [];

    wyjazdyData.forEach(function(akcja) {
        eventList.push({
            title: '🚒 Akcja #' + akcja.numer,
            start: akcja.start,
            end: akcja.end,
            url: akcja.url,
            backgroundColor: '#dc2626',
            borderColor: '#b91c1c',
            textColor: '#ffffff'
        });
    });

    pojazdyData.forEach(function(woz) {
        if (woz.data_przegladu) {
            eventList.push({ title: '🔧 Przegląd: ' + woz.nazwa, start: woz.data_przegladu, allDay: true, backgroundColor: '#2563eb', borderColor: '#1d4ed8', textColor: '#ffffff' });
        }
        if (woz.data_oc) {
            eventList.push({ title: '📄 Polisa OC: ' + woz.nazwa, start: woz.data_oc, allDay: true, backgroundColor: '#9333ea', borderColor: '#7e22ce', textColor: '#ffffff' });
        }
    });

    strazacyData.forEach(function(strazak) {
        if (strazak.data_badan) {
            eventList.push({ title: '👨🏻‍⚕️ Badania: ' + strazak.pelne_nazwisko, start: strazak.data_badan, allDay: true, backgroundColor: '#16a34a', borderColor: '#15803d', textColor: '#ffffff' });
        }
    });

    wydarzeniaData.forEach(function(wyd) {
        id: wyd.id,
        eventList.push({
            id: wyd.id,
            title: '⭐ ' + wyd.nazwa,
            start: wyd.data,
            allDay: true,
            backgroundColor: '#f59e0b',
            borderColor: '#d97706',
            textColor: '#ffffff',
            extendedProps: {
                notatki: wyd.notatki
            }
        });
    });

    window.currentClickedEvent = null;
    var form = document.getElementById('wydarzenieForm');

    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        locale: 'pl',
        firstDay: 1,
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek'
        },
        height: '650px',
        events: eventList,
        selectable: true,

        dateClick: function(info) {
            window.currentClickedEvent = null;
            form.reset();
            document.getElementById('modalWydarzenieId').value = '';
            
            document.getElementById('modalData').value = info.dateStr;
            document.getElementById('modalDataPokaz').value = info.dateStr.split('-').reverse().join('.');
            
            document.getElementById('btnUsunWydarzenie').style.display = 'none';
            document.getElementById('wydarzenieModal').style.display = 'flex';
        },
        
        eventClick: function(info) {
            if (info.event.url) {
                info.jsEvent.preventDefault();
                window.location.href = info.event.url;
            } else {
                form.reset();
                window.currentClickedEvent = info.event;
                
                document.getElementById('modalWydarzenieId').value = info.event.id;
                document.getElementById('modalData').value = info.event.startStr;
                document.getElementById('modalDataPokaz').value = info.event.startStr.split('-').reverse().join('.');
                
                form.elements['nazwa'].value = info.event.title.replace('⭐ ', '');
                form.elements['notatki'].value = info.event.extendedProps.notatki || '';
                
                document.getElementById('btnUsunWydarzenie').style.display = 'block';
                document.getElementById('wydarzenieModal').style.display = 'flex';
            }
        },

        eventDidMount: function(info) {
            if (info.event.extendedProps.notatki) {
                info.el.setAttribute('title', info.event.extendedProps.notatki);
            }
        }
    });
    
    calendar.render();

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        var formData = new FormData(form);
        
        fetch('/wydarzenia/zapisz/', {
            method: 'POST',
            body: formData,
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'sukces') {
                if (window.currentClickedEvent) {
                    window.currentClickedEvent.remove();
                    window.currentClickedEvent = null;
                }

                var dataWydarzenia = document.getElementById('modalData').value;
                calendar.addEvent({
                    id: data.id,
                    title: '⭐ ' + data.nazwa,
                    start: dataWydarzenia,
                    allDay: true,
                    backgroundColor: '#f59e0b',
                    borderColor: '#d97706',
                    textColor: '#ffffff',
                    extendedProps: {
                        notatki: data.notatki
                    }
                });
                
                var kontener = document.getElementById('kontener-najblizszych-wydarzen');
                if (kontener) {
                    var czesciDaty = dataWydarzenia.split('-');
                    var sformatowanaData = czesciDaty[2] + '.' + czesciDaty[1] + '.' + czesciDaty[0];
                    
                    var nowyWpisHTML = `
                        <div style="border-bottom: 1px solid #eee; margin-bottom: 10px; padding-bottom: 5px;">
                            <strong><i class="fas fa-star" style="color: #f59e0b;"></i> ${data.nazwa}</strong> <br>
                            <span style="font-size: 0.9rem; color: #555;">
                                Data: <b style="color: #1e293b;">${sformatowanaData}</b>
                            </span>
                    `;
                    
                    if (data.notatki) {
                        nowyWpisHTML += `
                            <div style="font-size: 0.85rem; color: #666; font-style: italic; margin-top: 2px;">
                                ${data.notatki}
                            </div>
                        `;
                    }
                    
                    nowyWpisHTML += `</div>`;
                    
                    var pTekst = document.getElementById('brak-wydarzen-tekst');
                    if (pTekst) {
                        pTekst.remove();
                    }
                    
                    kontener.insertAdjacentHTML('afterbegin', nowyWpisHTML);
                }
                
                document.getElementById('wydarzenieModal').style.display = 'none';
                form.reset();
            }
        });
    });

    document.getElementById('btnUsunWydarzenie').addEventListener('click', function() {
        var wydarzenieId = document.getElementById('modalWydarzenieId').value;
        
        if (wydarzenieId && confirm("Czy na pewno chcesz usunąć to wydarzenie?")) {
            var formData = new FormData();
            formData.append('wydarzenie_id', wydarzenieId);
            formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);

            fetch('/wydarzenia/usun/', {
                method: 'POST',
                body: formData,
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'sukces') {
                    if (window.currentClickedEvent) {
                        window.currentClickedEvent.remove();
                        window.currentClickedEvent = null;
                    }
                    zamknijModal();
                }
            });
        }
    });
});

function zamknijModal() {
    document.getElementById('wydarzenieModal').style.display = 'none';
}