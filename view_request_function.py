@app.route('/view_request/<int:request_id>')
@login_required
def view_request(request_id):
    # Get request details
    if current_user.role == 'student':
        query = """
            SELECT r.*, u.name as decided_by, 
                   DATE_FORMAT(r.updated_at, '%%Y-%%m-%%d %%H:%%i') as decided_at
            FROM od_requests r
            LEFT JOIN users u ON r.decided_by_id = u.id
            WHERE r.id = %s AND r.student_id = %s
        """
        cursor.execute(query, (request_id, current_user.id))
    else:  # teacher
        query = """
            SELECT r.*, u.name as decided_by,
                   DATE_FORMAT(r.updated_at, '%%Y-%%m-%%d %%H:%%i') as decided_at
            FROM od_requests r
            LEFT JOIN users u ON r.decided_by_id = u.id
            WHERE r.id = %s
        """
        cursor.execute(query, (request_id,))
    
    request = cursor.fetchone()
    
    if not request:
        flash('Request not found or access denied.', 'danger')
        return redirect(url_for(f'{current_user.role}_dashboard'))
    
    # Get comments
    query = """
        SELECT c.*, u.name as author, DATE_FORMAT(c.created_at, '%%Y-%%m-%%d %%H:%%i') as formatted_date
        FROM comments c
        JOIN users u ON c.user_id = u.id
        WHERE c.request_id = %s
        ORDER BY c.created_at DESC
    """
    cursor.execute(query, (request_id,))
    comments = cursor.fetchall()
    
    return render_template('view_request.html', request=request, comments=comments)
