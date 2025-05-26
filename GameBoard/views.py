from django.shortcuts import render, redirect, get_object_or_404
import json
from django.http import HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
# Create your views here.
from .models import Board, Game
from .forms import BoardForm

@login_required
def create_or_edit_board(request, board_id=None):
    if board_id:
        board = get_object_or_404(Board, id=board_id, user=request.user) 
    else:
        board = None

    if request.method == 'POST':
        form = BoardForm(request.POST, instance=board)
        if form.is_valid():
            gameboard = form.save(commit=False)
            gameboard.user = request.user

            dots = json.loads(request.POST.get('dots', "[]"))

            for dot in dots:
                if dot['col'] >= form.cleaned_data['columns'] or dot['row'] >= form.cleaned_data['rows']:
                    return HttpResponseBadRequest()
                
            gameboard.dots = request.POST.get('dots', "[]")

            gameboard.save()
            
            return redirect('home')  # Redirect to a list of boards or another page
            # to do board_list
    else:
        form = BoardForm(instance=board)

    dots = []
    rows = 0
    columns = 0
    if board and board.dots:
        dots = json.loads(board.dots)  # zakładam, że dots są zapisane jako JSON string
        rows = board.rows
        columns = board.columns

    context = {
        "form": form,
        "board": board,
        "dots_json": json.dumps(dots),
        "rows": rows,
        "columns": columns,
    }

    return render(request, 'edit.html', context)


@login_required
def home(request):
    boards = Board.objects.filter(user=request.user)
    all_boards = Board.objects.all()
    context = {
        'boards': boards,
        'all_boards': all_boards,
    }
    return render(request, 'home_page.html', context)

@login_required
def delete_board(request, board_id):
    board = get_object_or_404(Board, id=board_id, user=request.user)
    if request.method == 'POST':
        board.delete()
        return redirect('home')
    return render(request, 'home_page.html', {'message': 'Are you sure you want to delete this board?'})

# nie przenosi po usunięciu do home_page.html

@login_required
def solve_board(request, board_id):
    board = get_object_or_404(Board, id=board_id)
    board_data = {
        'id': board.id,
        'name': board.board_name,
        'rows': board.rows,
        'columns': board.columns,
        'dots': json.loads(board.dots) if board.dots else []
    }
    board_json = json.dumps(board_data)

    game = Game.objects.filter(board=board, user=request.user).first()
    game_dots = []
    if game:
        game_dots = json.loads(game.dots) if game.dots else []
    return render(request, 'solve.html', {'board': board_json, 'game_dots': json.dumps(game_dots)})


@login_required
def save_game(request):
    dots = request.POST.get('save_dots', "[]")
    print(dots)
    board = request.POST.get('board', None)
    if not board:
        return HttpResponseBadRequest("No board provided")
    board_data = json.loads(board)
    board_id = board_data.get('id')
    print(board_id)
    board = get_object_or_404(Board, id=board_id)
    game = Game.objects.filter(board=board, user=request.user).first()
    if not game:
        game = Game(board=board, user=request.user)
    game.dots = dots
    game.save()
    return redirect('home')